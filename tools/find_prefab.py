"""Find the Addressables bundle holding a prefab and dump its hierarchy: transforms, meshes, materials, scripts.

Usage: python find_prefab.py <aa folder> <prefab name substring>
"""
import os, sys
import UnityPy

aa, needle = sys.argv[1], sys.argv[2].lower()


def script_name(mb):
    try:
        return mb.m_Script.read().m_ClassName
    except Exception:
        return "?"


def dump(go, depth=0):
    comps = []
    for c in go.m_Component:
        o = c.component if hasattr(c, "component") else c[1]
        try:
            obj = o.read()
        except Exception:
            comps.append("?"); continue
        t = obj.object_reader.type.name
        if t == "MonoBehaviour":
            comps.append("MB:" + script_name(obj))
        elif t == "MeshFilter":
            try:
                m = obj.m_Mesh.read() if obj.m_Mesh else None
                comps.append(f"MeshFilter({m.m_Name if m else None})")
            except Exception:
                comps.append("MeshFilter(builtin)")
        elif t == "MeshRenderer":
            mats = []
            for mp in obj.m_Materials:
                try:
                    mat = mp.read(); mats.append(f"{mat.m_Name}<{mat.m_Shader.read().m_ParsedForm.m_Name if mat.m_Shader else '?'}>")
                except Exception:
                    mats.append("ext")
            comps.append("MeshRenderer[" + ", ".join(mats) + "]")
        elif t != "Transform":
            comps.append(t)
    tr = next(c for c in go.m_Component if (c.component if hasattr(c, "component") else c[1]).read().object_reader.type.name == "Transform")
    tr = (tr.component if hasattr(tr, "component") else tr[1]).read()
    print("  " * depth + f"- {go.m_Name}  pos={tuple(round(v, 3) for v in (tr.m_LocalPosition.x, tr.m_LocalPosition.y, tr.m_LocalPosition.z))} scale={tuple(round(v, 3) for v in (tr.m_LocalScale.x, tr.m_LocalScale.y, tr.m_LocalScale.z))}  {comps}")
    for child in tr.m_Children:
        dump(child.read().m_GameObject.read(), depth + 1)


for root, _, files in os.walk(aa):
    for f in files:
        if not f.endswith(".bundle"):
            continue
        p = os.path.join(root, f)
        try:
            env = UnityPy.load(p)
            hits = [k for k in env.container if needle in k.lower()]
        except Exception:
            continue
        if hits:
            print("BUNDLE", p, os.path.getsize(p))
            for k in hits:
                print(" container", k)
                obj = env.container[k].read()
                if obj.object_reader.type.name == "GameObject":
                    dump(obj)
            sys.exit(0)
print("not found")
