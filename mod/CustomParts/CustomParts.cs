using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using Il2CppInterop.Runtime;
using MelonLoader;
using UnityEngine;
using UnityEngine.AddressableAssets;
using UnityEngine.AddressableAssets.ResourceLocators;
using UnityEngine.ResourceManagement.ResourceLocations;
using Il2CppLocations = Il2CppSystem.Collections.Generic.IList<UnityEngine.ResourceManagement.ResourceLocations.IResourceLocation>;

[assembly: MelonInfo(typeof(CustomParts.CustomPartsMod), "PCBS2 CustomParts", "0.2.1", "MegaParts")]
[assembly: MelonGame(null, "PCBS2")]

namespace CustomParts
{
    /// <summary>One custom part from Mods\CustomParts\parts.txt (field list is in that file).</summary>
    sealed class Part
    {
        public string Id, Key, BaseKey, Bundle, Prefab;
        public float StockMm, ModelMm, UnitsPerM; // UnitsPerM > 0: fixed scale instead of the stock shroud's length
        public (string Stock, string Model) Shroud, Bracket, Top, Board;
        public string[] Hide;
        public (string Model, string Stock)[] Fans, Moves;
        public AssetBundle Asset;
        public GameObject Loaded;
        public bool Registered;
        public Vector3 RotDeg;   // extra turn in degrees about the card's length, height and thickness axes
        public Vector3 OffsetMm; // x = toward bracket, y = up (toward power connector), z = toward the fans (away from the board)
        // Per-build tuning (case/motherboard key -> offset, rotation), from builds.txt; wins over the two above.
        public readonly Dictionary<string, (Vector3 Off, Vector3 Rot)> Builds = new();
    }

    sealed class FanLink { public Transform Model, Stock; public Quaternion Last; public Vector3 Hub, Axis; }

    /// <summary>
    /// Adds parts that have their own Asset Path key. The key is registered in the game's Addressables
    /// locator list, pointing at the stock base prefab's bundle location, so the game loads and spawns the
    /// part through its normal Addressables path (a separate part with its own row, slots from its XML).
    /// The game's part behaviour lives in that stock prefab and can't be authored outside the game, so each
    /// spawned instance (root named after the part ID) gets its stock visuals replaced by the bundle model,
    /// oriented, scaled and placed automatically from reference parts on both models, and its root collider
    /// refitted. The stock base part itself is never touched.
    /// </summary>
    public partial class CustomPartsMod : MelonMod
    {
        const string Marker = "__CustomPart";
        readonly List<Part> parts = new();
        readonly List<FanLink> fans = new();
        readonly Dictionary<int, Vector3> movedFrom = new(); // stock object -> its original local position
        float nextTry;

        public override void OnInitializeMelon()
        {
            var dir = Path.Combine(MelonLoader.Utils.MelonEnvironment.ModsDirectory, "CustomParts");
            var cfg = cfgPath = Path.Combine(dir, "parts.txt");
            if (File.Exists(cfg)) cfgTime = File.GetLastWriteTimeUtc(cfg);
            if (!File.Exists(cfg)) { LoggerInstance.Warning($"No {cfg}"); return; }
            foreach (var p in ReadConfig(cfg))
            {
                p.Asset = parts.FirstOrDefault(x => x.Bundle == p.Bundle)?.Asset ?? AssetBundle.LoadFromFile(Path.Combine(dir, p.Bundle));
                if (p.Asset == null) { LoggerInstance.Error($"[{p.Id}] can't load bundle {p.Bundle}"); continue; }
                if (!Reload(p)) { LoggerInstance.Error($"[{p.Id}] no prefab {p.Prefab} in {p.Bundle}"); continue; }
                parts.Add(p);
                LoggerInstance.Msg($"[{p.Id}] model {p.Prefab} loaded from {p.Bundle}");
            }
            buildsPath = Path.Combine(dir, "builds.txt");
            LoadBuilds();
            if (parts.Count > 0) PatchSpawns();
        }

        IEnumerable<Part> ReadConfig(string cfg)
        {
            foreach (var raw in File.ReadAllLines(cfg))
            {
                var line = raw.Trim();
                if (line.Length == 0 || line.StartsWith("#")) continue;
                var f = line.Split('|').Select(x => x.Trim()).ToArray();
                if (f.Length < 11) { LoggerInstance.Warning($"Bad line (need 11+ fields): {line}"); continue; }
                bool fixedScale = f[5].StartsWith("@");
                // "bracket" as the custom size: scale the model so its bracket is a standard 120.02 mm full-height bracket.
                var mm = f[5].TrimStart('@').Split('/').Select(x => x.Trim().Equals("bracket", StringComparison.OrdinalIgnoreCase) ? -1f : float.Parse(x, CultureInfo.InvariantCulture)).ToArray();
                yield return new Part
                {
                    Id = f[0], Key = f[1], BaseKey = f[2], Bundle = f[3], Prefab = f[4],
                    StockMm = fixedScale ? 0 : mm[0], UnitsPerM = fixedScale ? mm[0] : 0, ModelMm = mm.Length > 1 ? mm[1] : mm[0],
                    Shroud = Pair(f[6]), Bracket = Pair(f[7]), Top = Pair(f[8]), Board = Pair(f[9]),
                    Hide = f[10].Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries),
                    Fans = Pairs(f, 11), Moves = Pairs(f, 12),
                    OffsetMm = Offset(f, 13),
                    RotDeg = Offset(f, 14),
                };
            }
        }

        static Vector3 Offset(string[] f, int i)
        {
            if (f.Length <= i) return Vector3.zero;
            var n = f[i].Split(' ', StringSplitOptions.RemoveEmptyEntries).Select(x => float.Parse(x, CultureInfo.InvariantCulture)).ToArray();
            return new Vector3(n.ElementAtOrDefault(0), n.ElementAtOrDefault(1), n.ElementAtOrDefault(2));
        }

        // parts.txt is re-read when saved: new offsets apply to every fitted card within a second (no restart).
        string cfgPath;
        DateTime cfgTime;

        void HotReload()
        {
            var t = File.GetLastWriteTimeUtc(cfgPath);
            if (t == cfgTime) return;
            cfgTime = t;
            try
            {
                foreach (var n in ReadConfig(cfgPath))
                {
                    var p = parts.FirstOrDefault(x => x.Id == n.Id);
                    if (p != null) (p.OffsetMm, p.RotDeg) = (n.OffsetMm, n.RotDeg);
                }
            }
            catch (Exception ex) { LoggerInstance.Error($"parts.txt: {ex.Message}"); return; }
            Refit(_ => true);
            LoggerInstance.Msg("parts.txt reloaded");
        }

        // Rebuild the model on every fitted instance of the matching parts, with the current settings.
        void Refit(Func<Part, bool> which) => Refit((p, _) => which(p));

        void Refit(Func<Part, Transform, bool> which)
        {
            foreach (var (p, root, stock) in fitted.Where(x => x.Root != null && which(x.Part, x.Root)).ToList())
            {
                if (root == null) continue;
                var h = root.Find(Marker);
                if (h == null) continue;
                fans.RemoveAll(x => x.Model == null || x.Model.IsChildOf(h));
                h.name = Marker + "_old"; // Destroy is deferred to the end of the frame; rename so Fit builds a fresh one
                UnityEngine.Object.Destroy(h.gameObject);
                fitted.RemoveAll(x => x.Root == root);
                Fit(p, root);
            }
        }

        static (string, string) Pair(string s) { var x = s.Split('='); return (x[0].Trim(), x.Length > 1 ? x[1].Trim() : ""); }
        static (string, string)[] Pairs(string[] f, int i) =>
            f.Length <= i ? Array.Empty<(string, string)>() :
            f[i].Split(',', StringSplitOptions.RemoveEmptyEntries).Where(x => x.Contains('=')).Select(Pair).ToArray();

        public override void OnUpdate()
        {
            SpinFans();
            KeepHidden();
            Tune();
            if (parts.Count == 0 || Time.unscaledTime < nextTry) return;
            nextTry = Time.unscaledTime + 1f;
            foreach (var p in parts.Where(x => !x.Registered)) Register(p);
            HotReload();
            Scan();
            CheckSlots();
        }

        // ---- Addressables: make the new key resolve ----

        static Il2CppSystem.Object Key(string s) => new Il2CppSystem.Object(IL2CPP.ManagedStringToIl2Cpp(s));

        static List<IResourceLocator> Locators()
        {
            var list = new List<IResourceLocator>();
            var en = Addressables.ResourceLocators.GetEnumerator();
            var walk = new Il2CppSystem.Collections.IEnumerator(en.Pointer);
            while (walk.MoveNext()) list.Add(en.Current);
            return list;
        }

        static Il2CppLocations Locate(IEnumerable<IResourceLocator> locators, string key)
        {
            if (string.IsNullOrEmpty(key)) return null;
            foreach (var type in new[] { Il2CppType.Of<GameObject>(), null })
                foreach (var l in locators)
                    if (l.Locate(Key(key), type, out var found) && found != null && Count(found) > 0) return found;
            return null;
        }

        static int Count(Il2CppLocations l) => new Il2CppSystem.Collections.Generic.ICollection<IResourceLocation>(l.Pointer).Count;

        // The game may load a part by its row's Asset Path or by the address it derives from it,
        // so the base part's and our part's are both tried / registered.
        static (string Path, string Address) Desc(Func<Il2Cpp.PartsDatabase, Il2Cpp.PartDesc> get)
        {
            var db = Il2Cpp.PartsDatabase.s_instance;
            var d = db == null ? null : get(db);
            return d == null ? (null, null) : (d.m_assetPath, d.m_address);
        }

        int tries;

        // Retried every second until the game's own catalog and part table are loaded.
        void Register(Part p)
        {
            try
            {
                tries++;
                var locators = Locators();
                var baseDesc = Desc(db => db.GetPartFromPath(p.BaseKey, false));
                var ourDesc = Desc(db => db.GetPartFromID(p.Id));
                string baseKey = null; Il2CppLocations baseLocs = null;
                foreach (var k in new[] { p.BaseKey, baseDesc.Address, baseDesc.Path })
                    if ((baseLocs = Locate(locators, k)) != null) { baseKey = k; break; }
                if (baseLocs == null || ourDesc.Path == null)
                {
                    // Diagnose once only: walking the locators again later crashed the game (native access
                    // violation) when the XML Part Loader was missing and our part row never appeared.
                    if (tries == 15) Diagnose(p, locators, baseDesc, ourDesc);
                    if (tries >= 60)
                    {
                        p.Registered = true; // give up: stop retrying so nothing keeps touching the catalog
                        LoggerInstance.Error($"[{p.Id}] gave up after {tries} s: our part row '{p.Id}' never appeared " +
                                             "(is the XML Part Loader installed as version.dll or xpl_version.dll?)");
                    }
                    return; // not loaded yet
                }
                var ourKeys = new[] { p.Key, ourDesc.Path, ourDesc.Address }.Where(k => !string.IsNullOrEmpty(k)).Distinct().ToList();
                var map = new ResourceLocationMap("CustomParts:" + p.Id, ourKeys.Count);
                foreach (var k in ourKeys) map.Add(Key(k), baseLocs);
                Addressables.AddResourceLocator(new IResourceLocator(map.Pointer), null, null);
                p.Registered = true;
                LoggerInstance.Msg($"[{p.Id}] catalog registered: {string.Join(", ", ourKeys)} -> {baseKey} ({Count(baseLocs)} location(s), {locators.Count} locator(s))");
                var check = Locate(Locators(), ourKeys.Last());
                if (check != null) LoggerInstance.Msg($"[{p.Id}] key resolved: {ourKeys.Last()} -> {check[0].InternalId}");
                else LoggerInstance.Error($"[{p.Id}] key does NOT resolve after registering");
            }
            catch (Exception ex)
            {
                p.Registered = true; // one failure is enough to report
                LoggerInstance.Error($"[{p.Id}] catalog registration failed: {ex}");
            }
        }

        // Logged every 15 s while waiting: what the game's locators hold, so a key mismatch is visible.
        void Diagnose(Part p, List<IResourceLocator> locators, (string Path, string Address) baseDesc, (string Path, string Address) ourDesc)
        {
            LoggerInstance.Warning($"[{p.Id}] still waiting (try {tries}): {locators.Count} locator(s); base part path '{baseDesc.Path}' address '{baseDesc.Address}'; our part path '{ourDesc.Path}' address '{ourDesc.Address}'");
            var hint = p.BaseKey.Substring(p.BaseKey.LastIndexOf('/') + 1);
            foreach (var l in locators)
            {
                var sample = new List<string>();
                int n = 0;
                var en = l.Keys.GetEnumerator();
                var walk = new Il2CppSystem.Collections.IEnumerator(en.Pointer);
                while (walk.MoveNext())
                {
                    n++;
                    var k = en.Current?.ToString();
                    if (k != null && k.Contains(hint) && sample.Count < 5) sample.Add(k);
                }
                LoggerInstance.Warning($"  locator '{l.LocatorId}': {n} keys; matching '{hint}': {string.Join(" | ", sample)}");
            }
        }

        // ---- Spawned instances: put the model on ----

        // Fitted instances and the stock renderers hidden on each. The game re-enables part visuals on some
        // state changes (hover, install, preview), so they're re-hidden every frame: a cheap check, no search.
        readonly List<(Part Part, Transform Root, List<MeshRenderer> Stock)> fitted = new();

        void KeepHidden()
        {
            for (int i = fitted.Count - 1; i >= 0; i--)
            {
                var (_, root, stock) = fitted[i];
                try
                {
                    if (root == null) { fitted.RemoveAt(i); continue; }
                    foreach (var r in stock) if (r != null && !r.forceRenderingOff) r.forceRenderingOff = true;
                }
                catch { fitted.RemoveAt(i); } // destroyed
            }
        }

        // Harmony postfix on the game's part-spawn methods: fit in the same frame the part appears, so the stock
        // model is never drawn. The once-a-second scan stays as a fallback for spawn paths not patched here.
        static CustomPartsMod self;

        void PatchSpawns()
        {
            self = this;
            var post = new HarmonyLib.HarmonyMethod(typeof(CustomPartsMod).GetMethod(nameof(OnSpawned), System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic));
            int n = 0;
            foreach (var m in typeof(Il2Cpp.PartsDatabase).GetMethods())
            {
                if (m.ReturnType != typeof(GameObject) || !(m.Name is "InstantiatePart" or "InstantiateLoadedPart" or "InstantiateSubPart")) continue;
                try { HarmonyInstance.Patch(m, postfix: post); n++; }
                catch (Exception ex) { LoggerInstance.Warning($"Can't patch {m.Name}: {ex.Message}"); }
            }
            LoggerInstance.Msg($"Patched {n} part-spawn method(s)");
        }

        static void OnSpawned(GameObject __result)
        {
            try
            {
                if (__result == null) return;
                var p = self.parts.FirstOrDefault(x => x.Id == __result.name);
                if (p == null || __result.transform.Find(Marker) != null) return;
                self.Fit(p, __result.transform);
            }
            catch (Exception ex) { self.LoggerInstance.Error($"spawn fit failed: {ex}"); }
        }

        void Scan()
        {
            foreach (var t in UnityEngine.Object.FindObjectsByType<Transform>(FindObjectsSortMode.None))
            {
                var p = parts.FirstOrDefault(x => x.Id == t.name);
                if (p == null) continue;
                var holder = t.Find(Marker);
                if (holder == null) { try { Fit(p, t); } catch (Exception ex) { LoggerInstance.Error($"[{p.Id}] fit failed: {ex}"); } continue; }
                // The game re-enables part visuals on some state changes, so keep the stock meshes hidden.
                foreach (var r in StockRenderers(p, t)) if (!r.forceRenderingOff) r.forceRenderingOff = true;
            }
        }

        IEnumerable<MeshRenderer> StockRenderers(Part p, Transform root) =>
            root.GetComponentsInChildren<MeshRenderer>(true).Where(r =>
            {
                var m = r.GetComponent<MeshFilter>()?.sharedMesh;
                return m != null && p.Hide.Any(m.name.StartsWith) && r.transform.Find(Marker) == null && !IsUnder(r.transform, Marker);
            });

        static bool IsUnder(Transform t, string name) { for (; t != null; t = t.parent) if (t.name == name) return true; return false; }

        static Transform Child(Transform root, string name) =>
            root.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name && !IsUnder(t, Marker));
        static Transform ModelChild(Transform model, string name) =>
            model.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name == name);
        // Stock reference meshes are matched by mesh name (object names repeat), model ones by node name.
        static Transform StockMesh(Transform root, string mesh) =>
            root.GetComponentsInChildren<MeshFilter>(true).FirstOrDefault(f => f.sharedMesh != null && f.sharedMesh.name == mesh && !IsUnder(f.transform, Marker))?.transform
            ?? Child(root, mesh);

        void Fit(Part p, Transform root)
        {
            if (p.Loaded == null && !Reload(p)) { LoggerInstance.Error($"[{p.Id}] lost prefab {p.Prefab}"); return; }
            Transform need(Transform t, string what) => t ?? throw new Exception("reference not found: " + what);
            var slot = SlotOf(root);
            var build = BuildKey(slot);
            var (offMm, rotDeg, _) = Tuning(p, build);
            // Put stock objects moved by an earlier fit (the power connector) back first: the up axis is measured
            // from the connector, and measuring the moved one made each refit drift until the card turned 90 deg.
            foreach (var (_, st) in p.Moves)
            {
                var t = Child(root, st);
                if (t != null && movedFrom.TryGetValue(t.GetInstanceID(), out var orig)) t.localPosition = orig;
            }
            var sShroud = Bounds(root, need(StockMesh(root, p.Shroud.Stock), p.Shroud.Stock));
            var sBracket = Bounds(root, need(StockMesh(root, p.Bracket.Stock), p.Bracket.Stock));
            bool whole = p.Board.Stock == "*";
            var sAll = Bounds(root, StockRenderers(p, root).Cast<Renderer>());
            var sBoard = whole ? sAll : Bounds(root, need(StockMesh(root, p.Board.Stock), p.Board.Stock));
            var sTop = Center(root, need(Child(root, p.Top.Stock), p.Top.Stock));

            var stockRenderers = StockRenderers(p, root).ToList();
            var gameShader = stockRenderers.Select(r => r.sharedMaterial).FirstOrDefault(m => m != null)?.shader;
            // forceRenderingOff, not enabled = false: the game checks the stock renderers (suspected: the fan control app skips a Fan
            // whose fanRenderer is disabled), so they stay enabled and are just not drawn.
            foreach (var r in stockRenderers) r.forceRenderingOff = true;

            var holder = new GameObject(Marker).transform;
            holder.SetParent(root, false);
            var model = UnityEngine.Object.Instantiate(p.Loaded, holder).transform;
            model.localPosition = Vector3.zero; model.localRotation = Quaternion.identity; model.localScale = Vector3.one;
            // The bundle's HDRP/Lit is compiled for a different HDRP build; use the game's shader, keep textures.
            if (gameShader != null)
                foreach (var r in model.GetComponentsInChildren<Renderer>(true))
                    foreach (var m in r.materials) { m.shader = gameShader; m.SetColor("_EmissiveColor", Color.black); }

            Transform mref(string n) => need(ModelChild(model, n), n);
            // 1. Orientation: length axis = shroud's longest side, pointing toward the bracket; up = toward the
            //    power connector. Built the same way on both models, then the model is turned to match.
            var mShroud = Bounds(holder, mref(p.Shroud.Model));
            var (sL, sH) = Frame(sShroud, sBracket.center, sTop);
            var (mL, mH) = Frame(mShroud, Bounds(holder, mref(p.Bracket.Model)).center, Center(holder, mref(p.Top.Model)));
            model.localRotation = Quaternion.LookRotation(sL, sH) * Quaternion.Inverse(Quaternion.LookRotation(mL, mH));
            // Optional extra turn (field 15) about the card's own axes, for models the references can't orient.
            // Scale and alignment below run after it, so the card still lands on the bracket and slot.
            if (rotDeg != Vector3.zero)
            {
                int t0 = 3 - Axis(sL) - Axis(sH);
                var sT = Vector3.zero; sT[t0] = Mathf.Sign(sShroud.center[t0] - sBoard.center[t0]) is var g && g != 0 ? g : 1;
                model.localRotation = Quaternion.AngleAxis(rotDeg.x, sL) * Quaternion.AngleAxis(rotDeg.y, sH) * Quaternion.AngleAxis(rotDeg.z, sT) * model.localRotation;
            }

            // 2. Scale: game units per mm from the stock shroud, times the custom card's real length.
            int li = Axis(sL);
            float unitsPerMm = p.UnitsPerM > 0 ? p.UnitsPerM / 1000f : sShroud.size[li] / p.StockMm;
            float scale;
            if (p.ModelMm < 0)
            {
                float bh = Bounds(holder, mref(p.Bracket.Model)).size[Axis(sH)];
                scale = unitsPerMm * BracketMm / Mathf.Max(bh, 1e-6f);
            }
            else
            {
                float modelLen = Bounds(holder, mref(p.Shroud.Model)).size[li];
                scale = unitsPerMm * p.ModelMm / Mathf.Max(modelLen, 1e-6f);
            }
            model.localScale = Vector3.one * scale;

            // 3. Position: bracket outer face on the length axis, board bottom edge on the up axis,
            //    board plane on the thickness axis.
            int hi = Axis(sH), ti = 3 - li - hi;
            var mBracket = Bounds(holder, mref(p.Bracket.Model));
            var mBoard = whole ? Bounds(holder, model.GetComponentsInChildren<Renderer>(true)) : Bounds(holder, mref(p.Board.Model));
            var d = Vector3.zero;
            d[li] = Face(sBracket, li, Sign(sL, li)) - Face(mBracket, li, Sign(sL, li));
            d[hi] = Face(sBoard, hi, -Sign(sH, hi)) - Face(mBoard, hi, -Sign(sH, hi));
            if (whole)
            {
                // Merged body: bottoms (bracket tab) line up; on thickness the back faces (side away from the fans).
                var fan0 = p.Fans.Length > 0 ? Child(root, p.Fans[0].Stock) : null;
                float fs = fan0 != null ? Mathf.Sign(Center(root, fan0)[ti] - sAll.center[ti]) : 1;
                if (fs == 0) fs = 1;
                d[ti] = Face(sAll, ti, -fs) - Face(mBoard, ti, -fs);
            }
            else d[ti] = sBoard.center[ti] - mBoard.center[ti];
            // Per-part fine offset in mm along the card's own axes (field 14), for model detail the references
            // can't capture, e.g. a PCIe strip modelled on one face of the board instead of its middle.
            float fanSide = Mathf.Sign(sShroud.center[ti] - sBoard.center[ti]);
            d[li] += offMm.x * unitsPerMm * Sign(sL, li);
            d[hi] += offMm.y * unitsPerMm * Sign(sH, hi);
            d[ti] += offMm.z * unitsPerMm * (fanSide == 0 ? 1 : fanSide);
            model.localPosition += d;
            if (!whole) AlignmentReport(p, root, holder, model, p.Bracket, p.Board, li, hi, ti, sL, sH, unitsPerMm);

            foreach (var r in model.GetComponentsInChildren<Renderer>(true)) r.gameObject.layer = root.gameObject.layer;
            Link(p, root, model);

            // 4. Root collider (the one the player grabs and the case checks) = the new model's bounds, but no
            //    thicker than the row's Slot Size: a model a few mm over (bracket lip, fan frame) would otherwise
            //    reach into the next slot and block it. The board side stays put; the far side is trimmed.
            var all = Bounds(root, model.GetComponentsInChildren<Renderer>(true));
            var box = all;
            int slots = SlotSize(p);
            if (slots > 0)
            {
                float maxT = (slots * SlotPitchMm - 1f) * unitsPerMm;
                if (box.size[ti] > maxT)
                {
                    bool boardAtMin = Mathf.Abs(sBoard.center[ti] - box.min[ti]) < Mathf.Abs(sBoard.center[ti] - box.max[ti]);
                    var lo = box.min; var hi2 = box.max;
                    if (boardAtMin) hi2[ti] = lo[ti] + maxT; else lo[ti] = hi2[ti] - maxT;
                    box.SetMinMax(lo, hi2);
                }
            }
            foreach (var c in root.GetComponents<BoxCollider>()) { c.center = box.center; c.size = box.size; }
            // The case's PCI-cover check reads the slot count baked into the base prefab (3 on the 4090),
            // not the row, so set it from the row's Slot Size.
            int occBefore = -1;
            if (slots > 0)
                foreach (var cpc in root.GetComponentsInChildren<Il2Cpp.ComponentPC>(true))
                { occBefore = cpc.numberOfSlotsOccupied; cpc.numberOfSlotsOccupied = slots; }
            fitted.Add((p, root, StockRenderers(p, root).ToList()));
            fittedSlot[root.GetInstanceID()] = (slot == null ? 0 : slot.GetInstanceID(), build);

            var mm = all.size / unitsPerMm;
            if (!quiet) LoggerInstance.Msg($"[{p.Id}] prefab built on {root.name}: scale {scale:F4}, {unitsPerMm * 1000f:F3} units/m, " +
                               $"size {mm[li]:F0} x {mm[hi]:F0} x {mm[ti]:F0} mm (L x H x T, stock shroud {sShroud.size[li] / unitsPerMm:F0} x {sShroud.size[hi] / unitsPerMm:F0} x {sShroud.size[ti] / unitsPerMm:F0} mm), " +
                               $"collider {box.size[ti] / unitsPerMm:F0} mm thick = {Mathf.CeilToInt(box.size[ti] / unitsPerMm / SlotPitchMm - 0.05f)} slot(s) (row Slot Size {slots}), slots occupied {occBefore} -> {slots}, {root.GetComponents<BoxCollider>().Length} root collider(s) refitted");
        }

        // Diagnostic, once per part: after placement, how far each candidate reference face of the model is from
        // the matching stock face, in mm (0 = that pair lines up). Shows which reference to align on.
        readonly HashSet<string> reportedAlign = new();
        void AlignmentReport(Part p, Transform root, Transform holder, Transform model, (string Stock, string Model) bracket,
                             (string Stock, string Model) board, int li, int hi, int ti, Vector3 sL, Vector3 sH, float upm)
        {
            if (!reportedAlign.Add(p.Id)) return;
            var sb = Bounds(root, StockMesh(root, bracket.Stock)); var mb = Bounds(holder, ModelChild(model, bracket.Model));
            var sp = Bounds(root, StockMesh(root, board.Stock)); var mp = Bounds(holder, ModelChild(model, board.Model));
            string f(float v) => (v / upm).ToString("+0.0;-0.0", CultureInfo.InvariantCulture);
            float up = Sign(sH, hi), len = Sign(sL, li);
            LoggerInstance.Msg($"[{p.Id}] align mm (stock - model; + = toward bracket / up / +T):");
            LoggerInstance.Msg($"  L: bracket outer {f((Face(sb, li, len) - Face(mb, li, len)) * len)}, bracket inner {f((Face(sb, li, -len) - Face(mb, li, -len)) * len)}, board end {f((Face(sp, li, -len) - Face(mp, li, -len)) * len)}");
            LoggerInstance.Msg($"  H: board bottom {f((Face(sp, hi, -up) - Face(mp, hi, -up)) * up)}, bracket bottom {f((Face(sb, hi, -up) - Face(mb, hi, -up)) * up)}, bracket top {f((Face(sb, hi, up) - Face(mb, hi, up)) * up)}");
            LoggerInstance.Msg($"  T: board centre {f(sp.center[ti] - mp.center[ti])}, bracket min {f(sb.min[ti] - mb.min[ti])}, bracket max {f(sb.max[ti] - mb.max[ti])}, board min {f(sp.min[ti] - mp.min[ti])}, board max {f(sp.max[ti] - mp.max[ti])}");
            LoggerInstance.Msg($"  sizes mm: stock board {f(sp.size[li])} x {f(sp.size[hi])} x {f(sp.size[ti])}, model board {f(mp.size[li])} x {f(mp.size[hi])} x {f(mp.size[ti])}; stock bracket H {f(sb.size[hi])} T {f(sb.size[ti])}, model bracket H {f(mb.size[hi])} T {f(mb.size[ti])}");
        }

        const float SlotPitchMm = 20.32f; // PCIe slot spacing
        const float BracketMm = 120.02f;  // PCIe full-height bracket length (spec)

        static int SlotSize(Part p)
        {
            var d = Il2Cpp.PartsDatabase.s_instance?.GetPartFromID(p.Id)?.TryCast<Il2Cpp.PartDescGPU>();
            return d == null ? 0 : d.m_slotSize;
        }

        // Length direction (from shroud centre toward the bracket) and up direction (toward the top object),
        // each snapped to the box axis it lies on.
        static (Vector3, Vector3) Frame(Bounds shroud, Vector3 bracket, Vector3 top)
        {
            var s = shroud.size;
            int l = s.x >= s.y && s.x >= s.z ? 0 : s.y >= s.z ? 1 : 2;
            var L = Vector3.zero; L[l] = Mathf.Sign(bracket[l] - shroud.center[l]);
            // Up is the remaining axis the top object is furthest out along (relative to the shroud size).
            int h = -1; float best = -1;
            for (int i = 0; i < 3; i++)
            {
                if (i == l) continue;
                float off = Mathf.Abs(top[i] - shroud.center[i]) / Mathf.Max(s[i], 1e-6f);
                if (off > best) { best = off; h = i; }
            }
            var H = Vector3.zero; H[h] = Mathf.Sign(top[h] - shroud.center[h]);
            return (L, H);
        }

        static int Axis(Vector3 v) => Mathf.Abs(v.x) > 0.5f ? 0 : Mathf.Abs(v.y) > 0.5f ? 1 : 2;
        static float Sign(Vector3 v, int i) => Mathf.Sign(v[i]);
        static float Face(Bounds b, int i, float sign) => sign > 0 ? b.max[i] : b.min[i];

        void Link(Part p, Transform root, Transform model)
        {
            foreach (var (m, st) in p.Fans)
            {
                var mt = ModelChild(model, m); var stt = Child(root, st);
                var mesh = mt?.GetComponent<MeshFilter>()?.sharedMesh;
                if (mesh == null || stt == null) { LoggerInstance.Warning($"[{p.Id}] fan pair {m}={st} not found"); continue; }
                var ext = mesh.bounds.extents; // spin axis = the fan's thinnest side
                var axis = ext.x <= ext.y && ext.x <= ext.z ? Vector3.right : ext.y <= ext.z ? Vector3.up : Vector3.forward;
                fans.Add(new FanLink { Model = mt, Stock = stt, Last = stt.localRotation, Hub = mesh.bounds.center, Axis = axis });
            }
            // Stock objects such as the power connector move onto the model part, so cables plug in where it shows the socket.
            foreach (var (m, st) in p.Moves)
            {
                var mt = ModelChild(model, m); var stt = Child(root, st);
                if (mt == null || stt == null) { LoggerInstance.Warning($"[{p.Id}] move pair {m}={st} not found"); continue; }
                movedFrom.TryAdd(stt.GetInstanceID(), stt.localPosition);
                var before = stt.position;
                stt.position += Center(root, mt, world: true) - Center(root, stt, world: true);
                if (!quiet) LoggerInstance.Msg($"[{p.Id}] moved {st} by {(stt.position - before).magnitude:F3} onto {m}");
            }
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

        // ---- Bounds helpers (all in the given space's local coordinates) ----

        static Vector3 Center(Transform space, Transform t, bool world = false)
        {
            var r = t.GetComponentsInChildren<Renderer>(true);
            var c = r.Length > 0 ? space.TransformPoint(Bounds(space, r).center) : t.position;
            return world ? c : space.InverseTransformPoint(c);
        }

        static Bounds Bounds(Transform space, Transform t) => Bounds(space, new[] { t.GetComponent<Renderer>() }.Where(r => r != null).Concat(t.GetComponentsInChildren<Renderer>(true)).Distinct());

        static Bounds Bounds(Transform space, IEnumerable<Renderer> renderers)
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
                    var pt = space.InverseTransformPoint(r.transform.TransformPoint(corner));
                    if (!any) { b = new Bounds(pt, Vector3.zero); any = true; } else b.Encapsulate(pt);
                }
            }
            return b;
        }

        // ---- Bundle loading (same workaround as CustomModels) ----

        // The game's managed LoadAsset overloads are stripped, and the interop wrapper of the native call can't
        // build Unity 6's string span, so build the span from a pinned string and call the native binding directly.
        static unsafe UnityEngine.Object LoadAsset(AssetBundle bundle, string name)
        {
            const System.Reflection.BindingFlags any = System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic;
            var injected = typeof(AssetBundle).GetMethod("LoadAsset_Internal_Injected", any);
            var unmarshal = typeof(UnityEngine.Bindings.Unmarshal).GetMethod("UnmarshalUnityObject", any).MakeGenericMethod(typeof(UnityEngine.Object));
            var self = typeof(UnityEngine.Object.MarshalledUnityObject).GetMethod("MarshalNotNull", any).MakeGenericMethod(typeof(AssetBundle)).Invoke(null, new object[] { bundle });
            fixed (char* chars = name)
            {
                object span = new UnityEngine.Bindings.ManagedSpanWrapper(chars, name.Length);
                var handle = injected.Invoke(null, new object[] { self, span, Il2CppType.Of<GameObject>() });
                return (UnityEngine.Object)unmarshal.Invoke(null, new[] { handle });
            }
        }

        // Scene changes unload assets nothing references, so pin the prefab and reload it if it went anyway.
        static bool Reload(Part p)
        {
            p.Loaded = LoadAsset(p.Asset, p.Prefab)?.TryCast<GameObject>();
            if (p.Loaded == null) return false;
            p.Loaded.hideFlags |= HideFlags.DontUnloadUnusedAsset;
            return true;
        }
    }
}
