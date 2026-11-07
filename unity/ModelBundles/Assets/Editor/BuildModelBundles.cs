// Batchmode builder for PCBS2 custom-model bundles.
// Run: Unity.exe -batchmode -quit -projectPath <this project> -executeMethod BuildModelBundles.Build
// Each folder under Assets/Models/<Name> with one .fbx becomes bundle "<name>.bundle" holding prefab "<Name>"
// with HDRP/Lit materials wired from the PNGs next to it (matched by name: Color/BaseColor, Normal, Metallic, Roughness, AO, Emissive).
// A folder with model.json instead (from tools/glb_to_unity.py) is rebuilt from that: node tree, meshes and PBR factors.
using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.HighDefinition;

public static class BuildModelBundles
{
    const string OutDir = "../../out/bundles";

    public static void Build()
    {
        EnsurePipeline();
        foreach (var dir in Directory.GetDirectories("Assets/Models"))
        {
            var name = Path.GetFileName(dir);
            var prefabPath = $"{dir}/{name}.prefab";
            var fbx = Directory.GetFiles(dir, "*.fbx").FirstOrDefault();
            if (fbx != null)
            {
                FixTextureImport(dir);
                MakePrefab(dir, fbx.Replace('\\', '/'), prefabPath);
            }
            else if (File.Exists($"{dir}/model.json")) MakePrefabFromJson(dir, name, prefabPath);
            else continue;
            AssetImporter.GetAtPath(prefabPath).SetAssetBundleNameAndVariant(name.ToLowerInvariant(), "");
        }
        Directory.CreateDirectory(OutDir);
        BuildPipeline.BuildAssetBundles(OutDir, BuildAssetBundleOptions.ChunkBasedCompression, BuildTarget.StandaloneWindows64);
        Debug.Log("[ModelBundles] done");
    }

    // HDRP needs an active pipeline asset so HDRP/Lit variants are compiled into the bundle.
    static void EnsurePipeline()
    {
        if (GraphicsSettings.defaultRenderPipeline is HDRenderPipelineAsset) return;
        var asset = ScriptableObject.CreateInstance<HDRenderPipelineAsset>();
        AssetDatabase.CreateAsset(asset, "Assets/HDRPAsset.asset");
        GraphicsSettings.defaultRenderPipeline = asset;
        QualitySettings.renderPipeline = asset;
        AssetDatabase.SaveAssets();
    }

    static void FixTextureImport(string dir)
    {
        foreach (var png in Directory.GetFiles(dir, "*.png"))
        {
            var imp = (TextureImporter)AssetImporter.GetAtPath(png.Replace('\\', '/'));
            var lower = png.ToLowerInvariant();
            bool linear = !(lower.Contains("color") || lower.Contains("emissive"));
            bool normal = lower.Contains("normal");
            if (imp.sRGBTexture == !linear && (imp.textureType == TextureImporterType.NormalMap) == normal) continue;
            imp.sRGBTexture = !linear;
            imp.textureType = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
            imp.maxTextureSize = 2048;
            imp.SaveAndReimport();
        }
    }

    static Texture2D Tex(string dir, string prefix, params string[] keys)
    {
        foreach (var png in Directory.GetFiles(dir, prefix + "*.png"))
        {
            var n = Path.GetFileNameWithoutExtension(png).ToLowerInvariant();
            // The main set must not pick up a sub-part's maps (RTX_4090_FE_radiator_1_* also starts with RTX_4090_FE).
            if (n.Substring(prefix.Length).Contains("radiator")) continue;
            if (keys.Any(k => n.EndsWith(k.ToLowerInvariant())))
                return AssetDatabase.LoadAssetAtPath<Texture2D>(png.Replace('\\', '/'));
        }
        return null;
    }

    // HDRP mask map: R metallic, G AO, B detail mask, A smoothness. Baked from the separate maps.
    static Texture2D MaskMap(string dir, string prefix, Texture2D metal, Texture2D ao, Texture2D rough)
    {
        var path = $"{dir}/{prefix}_MaskMap.png";
        if (File.Exists(path)) return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        int size = 1024;
        Color[] Read(Texture2D t)
        {
            if (t == null) return null;
            var rt = RenderTexture.GetTemporary(size, size, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.Linear);
            Graphics.Blit(t, rt);
            var prev = RenderTexture.active; RenderTexture.active = rt;
            var tmp = new Texture2D(size, size, TextureFormat.RGBA32, false, true);
            tmp.ReadPixels(new Rect(0, 0, size, size), 0, 0);
            RenderTexture.active = prev; RenderTexture.ReleaseTemporary(rt);
            return tmp.GetPixels();
        }
        var m = Read(metal); var a = Read(ao); var r = Read(rough);
        var px = new Color[size * size];
        for (int i = 0; i < px.Length; i++)
            px[i] = new Color(m?[i].r ?? 0f, a?[i].r ?? 1f, 1f, 1f - (r?[i].r ?? 0.5f));
        var outTex = new Texture2D(size, size, TextureFormat.RGBA32, false, true);
        outTex.SetPixels(px);
        File.WriteAllBytes(path, outTex.EncodeToPNG());
        AssetDatabase.ImportAsset(path);
        var imp = (TextureImporter)AssetImporter.GetAtPath(path);
        imp.sRGBTexture = false; imp.SaveAndReimport();
        return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
    }

    static Material MakeMaterial(string dir, string prefix)
    {
        var path = $"{dir}/{prefix}.mat";
        var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (mat == null)
        {
            mat = new Material(Shader.Find("HDRP/Lit"));
            AssetDatabase.CreateAsset(mat, path);
        }
        var color = Tex(dir, prefix, "Color_Map", "BaseColor");
        var normal = Tex(dir, prefix, "Normal_Map", "Normal");
        var metal = Tex(dir, prefix, "Metallic_Map", "Metallic");
        var rough = Tex(dir, prefix, "Roughness_Map", "Roughness");
        var ao = Tex(dir, prefix, "AO_Map", "AO");
        var emis = Tex(dir, prefix, "Emissive_Map", "Emissive");
        if (color) mat.SetTexture("_BaseColorMap", color);
        if (normal) { mat.SetTexture("_NormalMap", normal); mat.EnableKeyword("_NORMALMAP"); }
        if (metal || rough || ao)
        {
            mat.SetTexture("_MaskMap", MaskMap(dir, prefix, metal, ao, rough));
            mat.EnableKeyword("_MASKMAP");
            mat.SetFloat("_Metallic", 1f); mat.SetFloat("_Smoothness", 1f);
        }
        if (emis)
        {
            mat.SetTexture("_EmissiveColorMap", emis);
            mat.SetColor("_EmissiveColor", Color.white * 2f);
            mat.EnableKeyword("_EMISSIVE_COLOR_MAP");
        }
        HDMaterial.ValidateMaterial(mat);
        EditorUtility.SetDirty(mat);
        return mat;
    }

    [Serializable] class GModel { public GNode[] nodes; public GMesh[] meshes; public GMat[] materials; public string[] images; }
    [Serializable] class GNode { public string name; public int parent, mesh; public float[] t, r, s; }
    [Serializable] class GMesh { public string name; public float[] pos, nrm, uv; public GSub[] subs; }
    [Serializable] class GSub { public int[] idx; public int mat; }
    [Serializable] class GMat { public string name; public float[] color; public float metal, rough; public int tex; }

    static void MakePrefabFromJson(string dir, string name, string prefabPath)
    {
        var g = JsonUtility.FromJson<GModel>(File.ReadAllText($"{dir}/model.json"));
        var mats = g.materials.Select((m, i) =>
        {
            var mat = new Material(Shader.Find("HDRP/Lit")) { name = m.name };
            // glTF factors are linear; SetColor expects gamma in a linear project.
            mat.SetColor("_BaseColor", new Color(m.color[0], m.color[1], m.color[2], m.color[3]).gamma);
            mat.SetFloat("_Metallic", Mathf.Clamp01(m.metal));
            mat.SetFloat("_Smoothness", 1f - Mathf.Clamp01(m.rough));
            if (m.tex >= 0) mat.SetTexture("_BaseColorMap", AssetDatabase.LoadAssetAtPath<Texture2D>($"{dir}/{g.images[m.tex]}"));
            HDMaterial.ValidateMaterial(mat);
            AssetDatabase.CreateAsset(mat, $"{dir}/mat_{i}.mat");
            return mat;
        }).ToArray();

        var meshes = g.meshes.Select((gm, i) =>
        {
            int n = gm.pos.Length / 3;
            var mesh = new Mesh { name = gm.name, indexFormat = n > 65535 ? IndexFormat.UInt32 : IndexFormat.UInt16 };
            mesh.vertices = Enumerable.Range(0, n).Select(k => new Vector3(gm.pos[k * 3], gm.pos[k * 3 + 1], gm.pos[k * 3 + 2])).ToArray();
            mesh.normals = Enumerable.Range(0, n).Select(k => new Vector3(gm.nrm[k * 3], gm.nrm[k * 3 + 1], gm.nrm[k * 3 + 2])).ToArray();
            mesh.uv = Enumerable.Range(0, n).Select(k => new Vector2(gm.uv[k * 2], gm.uv[k * 2 + 1])).ToArray();
            mesh.subMeshCount = gm.subs.Length;
            for (int k = 0; k < gm.subs.Length; k++) mesh.SetTriangles(gm.subs[k].idx, k);
            mesh.RecalculateBounds();
            mesh.RecalculateTangents();
            AssetDatabase.CreateAsset(mesh, $"{dir}/mesh_{i}.asset");
            return mesh;
        }).ToArray();

        var root = new GameObject(name);
        var objs = g.nodes.Select(gn => new GameObject(gn.name)).ToArray();
        for (int i = 0; i < g.nodes.Length; i++)
        {
            var gn = g.nodes[i];
            var t = objs[i].transform;
            t.SetParent(gn.parent >= 0 ? objs[gn.parent].transform : root.transform, false);
            t.localPosition = new Vector3(gn.t[0], gn.t[1], gn.t[2]);
            t.localRotation = new Quaternion(gn.r[0], gn.r[1], gn.r[2], gn.r[3]);
            t.localScale = new Vector3(gn.s[0], gn.s[1], gn.s[2]);
            if (gn.mesh < 0) continue;
            objs[i].AddComponent<MeshFilter>().sharedMesh = meshes[gn.mesh];
            objs[i].AddComponent<MeshRenderer>().sharedMaterials =
                g.meshes[gn.mesh].subs.Select(sb => mats[Math.Max(sb.mat, 0)]).ToArray();
        }
        var b = new Bounds();
        foreach (var r in root.GetComponentsInChildren<Renderer>()) b.Encapsulate(r.bounds);
        Debug.Log($"[ModelBundles] {name} from model.json: bounds size {b.size} center {b.center}");
        PrefabUtility.SaveAsPrefabAsset(root, prefabPath);
        UnityEngine.Object.DestroyImmediate(root);
        AssetDatabase.SaveAssets();
    }

    static void MakePrefab(string dir, string fbx, string prefabPath)
    {
        var model = AssetDatabase.LoadAssetAtPath<GameObject>(fbx);
        var go = (GameObject)PrefabUtility.InstantiatePrefab(model);
        PrefabUtility.UnpackPrefabInstance(go, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
        var baseName = Path.GetFileNameWithoutExtension(fbx);
        var main = MakeMaterial(dir, baseName);
        // Submeshes whose material name mentions radiator_N get that texture set; everything else the main set.
        foreach (var r in go.GetComponentsInChildren<Renderer>(true))
        {
            var mats = r.sharedMaterials.Select(m =>
            {
                var n = (m ? m.name : r.name).ToLowerInvariant();
                for (int i = 1; i <= 9; i++)
                    if (n.Contains($"radiator_{i}") || n.Contains($"radiator{i}"))
                        return MakeMaterial(dir, $"{baseName}_radiator_{i}");
                return main;
            }).ToArray();
            Debug.Log($"[ModelBundles] {r.name}: {string.Join(", ", r.sharedMaterials.Select(m => m ? m.name : "null"))}");
            r.sharedMaterials = mats;
        }
        var b = new Bounds();
        foreach (var r in go.GetComponentsInChildren<Renderer>()) b.Encapsulate(r.bounds);
        Debug.Log($"[ModelBundles] {go.name} bounds size {b.size} center {b.center}");
        PrefabUtility.SaveAsPrefabAsset(go, prefabPath);
        UnityEngine.Object.DestroyImmediate(go);
        AssetDatabase.SaveAssets();
    }
}
