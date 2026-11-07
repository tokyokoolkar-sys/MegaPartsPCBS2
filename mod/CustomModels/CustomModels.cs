using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Il2CppInterop.Runtime;
using Il2CppInterop.Runtime.InteropTypes.Arrays;
using MelonLoader;
using UnityEngine;

[assembly: MelonInfo(typeof(CustomModels.CustomModelsMod), "PCBS2 CustomModels", "0.2.0", "MegaParts")]
[assembly: MelonGame(null, "PCBS2")]

namespace CustomModels
{
    /// <summary>
    /// One model replacement, read from Mods\CustomModels\models.txt:
    ///   bundle | prefab name in bundle | part root name (the part ID in a build; trailing * = prefix) | mesh-name prefixes to hide, comma-separated | yaw pitch roll [x y z offset]
    ///   | fans: model part=stock fan, ... | moves: model part=stock object, ...
    /// The file is re-read when saved, so rotation and offset can be tuned with the game running.
    /// Lines starting with # are comments. The rotation is applied before auto-fitting, for models exported on other axes.
    /// Fans spin with the (hidden) stock fan they're paired with; moved stock objects (power connectors and the like)
    /// are shifted onto the model part so cables plug in where the model shows the socket.
    /// </summary>
    sealed class Swap
    {
        public string Bundle, Prefab, RootPrefix;
        public string[] HidePrefixes;
        public bool Hides(string mesh) => HidePrefixes.Any(mesh.StartsWith);
        public Vector3 Euler, Offset;
        public (string Model, string Stock)[] Fans, Moves;
        public AssetBundle Asset;
        public GameObject Loaded;
    }

    /// <summary>A model fan following a stock fan's rotation, around the model fan's own hub.</summary>
    sealed class FanLink
    {
        public Transform Model, Stock;
        public Quaternion Last;
        public Vector3 Hub, Axis;
    }

    /// <summary>One placed model: what it swaps, where it sits before the offset, and the stock objects moved onto it.</summary>
    sealed class Placed
    {
        public Swap Swap;
        public GameObject Holder;
        public Transform Model;
        public Vector3 Base;
        public readonly List<Transform> Moved = new();
    }

    public partial class CustomModelsMod : MelonMod
    {
        const string Marker = "__CustomModel";
        readonly List<Swap> swaps = new();
        readonly List<FanLink> fans = new();
        readonly List<Placed> placed = new();
        string cfgPath;
        DateTime cfgTime;
        float nextScan;

        public override void OnInitializeMelon()
        {
            var dir = Path.Combine(MelonLoader.Utils.MelonEnvironment.ModsDirectory, "CustomModels");
            cfgPath = Path.Combine(dir, "models.txt");
            if (!File.Exists(cfgPath)) { LoggerInstance.Warning($"No {cfgPath}"); return; }
            cfgTime = File.GetLastWriteTimeUtc(cfgPath);
            foreach (var s in ReadConfig())
            {
                // Several parts may share one bundle, and Unity refuses to open a bundle twice.
                var bundle = swaps.FirstOrDefault(x => x.Bundle == s.Bundle)?.Asset
                             ?? AssetBundle.LoadFromFile(Path.Combine(dir, s.Bundle));
                if (bundle == null) { LoggerInstance.Error($"Can't load bundle {s.Bundle}"); continue; }
                s.Asset = bundle;
                if (!Reload(s)) { LoggerInstance.Error($"No prefab {s.Prefab} in {s.Bundle}"); continue; }
                swaps.Add(s);
                LoggerInstance.Msg($"Loaded {s.Prefab} from {s.Bundle} -> replaces {s.RootPrefix}");
            }
        }

        IEnumerable<Swap> ReadConfig()
        {
            foreach (var raw in File.ReadAllLines(cfgPath))
            {
                var line = raw.Trim();
                if (line.Length == 0 || line.StartsWith("#")) continue;
                var p = line.Split('|').Select(x => x.Trim()).ToArray();
                if (p.Length < 4) { LoggerInstance.Warning($"Bad line: {line}"); continue; }
                var e = new float[6];
                if (p.Length > 4)
                {
                    var nums = p[4].Split(' ', StringSplitOptions.RemoveEmptyEntries).Select(x => float.Parse(x, System.Globalization.CultureInfo.InvariantCulture)).ToArray();
                    Array.Copy(nums, e, Math.Min(nums.Length, 6));
                }
                yield return new Swap
                {
                    Bundle = p[0], Prefab = p[1], RootPrefix = p[2],
                    HidePrefixes = p[3].Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries),
                    Euler = new Vector3(e[1], e[0], e[2]), Offset = new Vector3(e[3], e[4], e[5]),
                    Fans = Pairs(p, 5), Moves = Pairs(p, 6),
                };
            }
        }

        // On save: take the new settings for already-loaded bundles and redo every swap.
        void HotReload()
        {
            var t = File.GetLastWriteTimeUtc(cfgPath);
            if (t == cfgTime) return;
            cfgTime = t;
            try
            {
                foreach (var n in ReadConfig())
                {
                    var s = swaps.FirstOrDefault(x => x.Bundle == n.Bundle && x.Prefab == n.Prefab && x.RootPrefix == n.RootPrefix);
                    if (s == null) { LoggerInstance.Warning($"New bundle {n.Bundle} needs a restart"); continue; }
                    (s.HidePrefixes, s.Euler, s.Offset, s.Fans, s.Moves) = (n.HidePrefixes, n.Euler, n.Offset, n.Fans, n.Moves);
                }
            }
            catch (Exception ex) { LoggerInstance.Error($"models.txt: {ex.Message}"); return; }
            Unplace(_ => true);
            LoggerInstance.Msg("models.txt reloaded");
        }

        // Remove matching models; the next scan places them again with the current settings.
        void Unplace(Func<Placed, bool> which)
        {
            foreach (var p in placed.Where(which).ToList())
            {
                if (p.Holder != null)
                {
                    fans.RemoveAll(f => f.Model == null || f.Model.IsChildOf(p.Holder.transform));
                    UnityEngine.Object.Destroy(p.Holder);
                }
                placed.Remove(p);
            }
        }

        static (string, string)[] Pairs(string[] p, int i) =>
            p.Length <= i ? Array.Empty<(string, string)>() :
            p[i].Split(',', StringSplitOptions.RemoveEmptyEntries)
                .Select(x => x.Split('=')).Where(x => x.Length == 2)
                .Select(x => (x[0].Trim(), x[1].Trim())).ToArray();

        public override void OnUpdate()
        {
            SpinFans();
            Tune();
            if (swaps.Count == 0 || Time.unscaledTime < nextScan) return;
            nextScan = Time.unscaledTime + 1f;
            HotReload();
            ReportGpus();
            foreach (var mf in UnityEngine.Object.FindObjectsByType<MeshFilter>(FindObjectsSortMode.None))
            {
                var mesh = mf.sharedMesh;
                if (mesh == null) continue;
                foreach (var s in swaps)
                {
                    if (!s.Hides(mesh.name)) continue;
                    var root = FindRoot(mf.transform, s.RootPrefix);
                    if (root == null) continue;
                    var holder = root.Find(Marker);
                    if (holder == null) { Apply(s, root); continue; }
                    // The game re-enables part visuals (e.g. on state changes), so keep stock meshes hidden.
                    var r = mf.GetComponent<MeshRenderer>();
                    if (r != null && r.enabled && !mf.transform.IsChildOf(holder)) r.enabled = false;
                }
            }
        }

        // Diagnostic: log each GPU part root (and its meshes) once, so unmatched swaps can be configured.
        readonly HashSet<string> reported = new();
        void ReportGpus()
        {
            foreach (var t in UnityEngine.Object.FindObjectsByType<Transform>(FindObjectsSortMode.None))
            {
                if (!t.name.StartsWith("GPU_") || t.parent == null || t.parent.name.StartsWith("GPU_")) continue;
                if (!reported.Add(t.name)) continue;
                var meshes = t.GetComponentsInChildren<MeshFilter>(true)
                    .Where(f => f.sharedMesh != null).Select(f => f.sharedMesh.name).Distinct();
                LoggerInstance.Msg($"GPU root {t.name} (parent {t.parent.name}): {string.Join(", ", meshes)}");
            }
        }

        // Unity 6 binds LoadAsset through a string span the interop wrapper can't marshal,
        // so call it via IL2CPP reflection and let the game's native code handle the string.
        // The game's managed LoadAsset overloads are stripped, and the interop wrapper of the native
        // call can't build Unity 6's string span. So build the span from a pinned string and call the
        // native binding (still in UnityPlayer.dll) through the wrapper's own pieces.
        static unsafe UnityEngine.Object LoadAsset(AssetBundle bundle, string name)
        {
            const System.Reflection.BindingFlags any = System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic;
            var injected = typeof(AssetBundle).GetMethod("LoadAsset_Internal_Injected", any);
            var unmarshal = typeof(UnityEngine.Bindings.Unmarshal).GetMethod("UnmarshalUnityObject", any).MakeGenericMethod(typeof(UnityEngine.Object));
            var self = typeof(UnityEngine.Object.MarshalledUnityObject).GetMethod("MarshalNotNull", any).MakeGenericMethod(typeof(AssetBundle)).Invoke(null, new object[] { bundle });
            fixed (char* chars = name)
            {
                object span = new UnityEngine.Bindings.ManagedSpanWrapper(chars, name.Length);
                var args = new object[] { self, span, Il2CppType.Of<GameObject>() };
                var handle = injected.Invoke(null, args);
                return (UnityEngine.Object)unmarshal.Invoke(null, new[] { handle });
            }
        }

        // Scene changes unload assets nothing references, so pin the prefab and reload it if it went anyway.
        static bool Reload(Swap s)
        {
            s.Loaded = LoadAsset(s.Asset, s.Prefab)?.TryCast<GameObject>();
            if (s.Loaded == null) return false;
            s.Loaded.hideFlags |= HideFlags.DontUnloadUnusedAsset;
            return true;
        }

        void SpinFans()
        {
            for (int i = fans.Count - 1; i >= 0; i--)
            {
                var f = fans[i];
                try
                {
                    var now = f.Stock.localRotation;
                    float angle = Quaternion.Angle(f.Last, now);
                    f.Last = now;
                    if (angle > 0f) f.Model.RotateAround(f.Model.TransformPoint(f.Hub), f.Model.TransformDirection(f.Axis), angle);
                }
                catch { fans.RemoveAt(i); } // part sold or unloaded
            }
        }

        static Transform FindChild(Transform root, string name) =>
            root.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name);

        void Link(Swap s, Transform root, Transform model, Placed placedModel)
        {
            foreach (var (m, st) in s.Fans)
            {
                var mt = FindChild(model, m); var stt = FindChild(root, st);
                var mesh = mt?.GetComponent<MeshFilter>()?.sharedMesh;
                if (mesh == null || stt == null) { LoggerInstance.Warning($"Fan pair {m}={st} not found"); continue; }
                // Spin axis = the fan mesh's thinnest side.
                var ext = mesh.bounds.extents;
                var axis = ext.x <= ext.y && ext.x <= ext.z ? Vector3.right : ext.y <= ext.z ? Vector3.up : Vector3.forward;
                fans.Add(new FanLink { Model = mt, Stock = stt, Last = stt.localRotation, Hub = mesh.bounds.center, Axis = axis });
            }
            foreach (var (m, st) in s.Moves)
            {
                var mr = FindChild(model, m)?.GetComponent<Renderer>(); var stt = FindChild(root, st);
                var sr = stt?.GetComponent<Renderer>();
                if (mr == null || sr == null) { LoggerInstance.Warning($"Move pair {m}={st} not found"); continue; }
                stt.position += mr.bounds.center - sr.bounds.center;
                placedModel.Moved.Add(stt);
            }
        }

        static Transform FindRoot(Transform t, string prefix)
        {
            for (; t != null; t = t.parent)
                if (prefix.EndsWith("*") ? t.name.StartsWith(prefix.TrimEnd('*')) : t.name == prefix) return t;
            return null;
        }

        void Apply(Swap s, Transform root)
        {
            if (s.Loaded == null && !Reload(s)) { LoggerInstance.Error($"Lost prefab {s.Prefab}"); return; }
            // Hide the stock visuals, keep screws, latches, colliders and scripts.
            var hidden = new List<Renderer>();
            foreach (var r in root.GetComponentsInChildren<MeshRenderer>(true))
            {
                var f = r.GetComponent<MeshFilter>();
                if (f != null && f.sharedMesh != null && s.Hides(f.sharedMesh.name)) hidden.Add(r);
            }
            var target = LocalBounds(root, hidden);
            // The bundle's own HDRP/Lit was compiled by a different HDRP build and renders garbage here;
            // switch to the game's copy (taken from the stock mesh) and keep the textures.
            var gameShader = hidden.Select(r => r.sharedMaterial).FirstOrDefault(m => m != null)?.shader;
            foreach (var r in hidden) r.enabled = false;

            var holder = new GameObject(Marker).transform;
            holder.SetParent(root, false);
            var model = UnityEngine.Object.Instantiate(s.Loaded, holder).transform;
            model.localRotation = Quaternion.Euler(s.Euler);
            model.localPosition = Vector3.zero;
            model.localScale = Vector3.one;
            if (gameShader != null)
                foreach (var r in model.GetComponentsInChildren<Renderer>(true))
                    foreach (var m in r.materials)
                    {
                        m.shader = gameShader;
                        m.SetColor("_EmissiveColor", Color.black);
                    }

            // Uniform scale so the longest side matches the stock card, then center on the stock bounds.
            var have = LocalBounds(root, model.GetComponentsInChildren<Renderer>(true).ToList());
            float scale = Max(target.size) / Mathf.Max(Max(have.size), 1e-6f);
            model.localScale = Vector3.one * scale;
            have = LocalBounds(root, model.GetComponentsInChildren<Renderer>(true).ToList());
            model.localPosition += target.center - have.center + s.Offset;
            foreach (var r in model.GetComponentsInChildren<Renderer>(true)) r.gameObject.layer = root.gameObject.layer;
            var pm = new Placed { Swap = s, Holder = holder.gameObject, Model = model, Base = model.localPosition - s.Offset };
            placed.Add(pm);
            Link(s, root, model, pm);
            var left = root.GetComponentsInChildren<Renderer>(true)
                .Where(r => r.enabled && r.gameObject.activeInHierarchy && !r.transform.IsChildOf(holder))
                .Select(r => r.name + "<" + (r.GetComponent<MeshFilter>()?.sharedMesh?.name ?? r.GetIl2CppType().Name) + ">");
            LoggerInstance.Msg($"Still visible on {root.name}: {string.Join(", ", left)}");
            LoggerInstance.Msg($"Swapped {root.name}: stock {target.size} -> model {have.size * 1f}, scale {scale:F4}");
        }

        static float Max(Vector3 v) => Mathf.Max(v.x, Mathf.Max(v.y, v.z));

        /// <summary>Bounds of the given renderers, expressed in root's local space.</summary>
        static Bounds LocalBounds(Transform root, List<Renderer> renderers)
        {
            bool any = false;
            var b = new Bounds();
            foreach (var r in renderers)
            {
                var f = r.GetComponent<MeshFilter>();
                if (f == null || f.sharedMesh == null) continue;
                var mb = f.sharedMesh.bounds;
                for (int i = 0; i < 8; i++)
                {
                    var corner = mb.center + Vector3.Scale(mb.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1));
                    var p = root.InverseTransformPoint(r.transform.TransformPoint(corner));
                    if (!any) { b = new Bounds(p, Vector3.zero); any = true; } else b.Encapsulate(p);
                }
            }
            return b;
        }
    }
}
