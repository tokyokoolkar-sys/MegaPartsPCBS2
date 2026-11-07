"""Unpack a .glb into model.json + images for the Unity bundle builder (Unity has no built-in glTF importer).

Usage: python glb_to_unity.py <model.glb> <out folder> [node to split in two ...]

model.json holds the node tree (local TRS), meshes (flat float/int arrays, one index list per primitive)
and PBR materials, already converted from glTF's right-handed axes to Unity's left-handed ones:
X is mirrored on positions, normals, translations and rotations, and triangle winding is flipped.
"""
import json, os, struct, sys
from array import array

COMPONENTS = {5120: "b", 5121: "B", 5122: "h", 5123: "H", 5125: "I", 5126: "f"}
WIDTH = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def read_glb(path):
    data = open(path, "rb").read()
    magic, _, _ = struct.unpack_from("<4sII", data, 0)
    assert magic == b"glTF", "not a .glb"
    off, gltf, binary = 12, None, b""
    while off < len(data):
        length, kind = struct.unpack_from("<I4s", data, off)
        chunk = data[off + 8: off + 8 + length]
        if kind == b"JSON":
            gltf = json.loads(chunk)
        elif kind == b"BIN\0":
            binary = chunk
        off += 8 + length
    assert gltf is not None, "no JSON chunk"
    return gltf, binary


def accessor(gltf, binary, i):
    a = gltf["accessors"][i]
    view = gltf["bufferViews"][a["bufferView"]]
    fmt, n = COMPONENTS[a["componentType"]], WIDTH[a["type"]]
    size = struct.calcsize(fmt)
    stride = view.get("byteStride") or size * n
    start = view.get("byteOffset", 0) + a.get("byteOffset", 0)
    out = array("d" if fmt == "f" else "l")
    for k in range(a["count"]):
        out.extend(struct.unpack_from(f"<{n}{fmt}", binary, start + k * stride))
    if a.get("normalized") and fmt != "f":
        top = float((1 << (size * 8 - (fmt.islower()))) - 1)
        out = array("d", (v / top for v in out))
    return list(out)


def mirror_x(values, n):
    """Negate the first component of every n-wide element."""
    for k in range(0, len(values), n):
        values[k] = -values[k]
    return values


def split_halves(nodes, meshes, name):
    """Cut node `name`'s mesh in two across its longest side, into nodes `name`_A and `name`_B.
    For models that merge several fans into one mesh: each half then spins about its own bounds centre."""
    node = next(n for n in nodes if n["name"] == name)
    mesh = meshes[node["mesh"]]
    pos = mesh["pos"]
    spans = [max(pos[a::3]) - min(pos[a::3]) for a in range(3)]
    axis = spans.index(max(spans))
    mid = (max(pos[axis::3]) + min(pos[axis::3])) / 2
    halves = []
    for side in (0, 1):
        remap, out = {}, {"name": f"{mesh['name']}_{'AB'[side]}", "pos": [], "nrm": [], "uv": [], "subs": []}
        for sub in mesh["subs"]:
            idx = []
            for k in range(0, len(sub["idx"]), 3):
                tri = sub["idx"][k:k + 3]
                if (sum(pos[v * 3 + axis] for v in tri) / 3 > mid) != bool(side):
                    continue
                for v in tri:
                    if v not in remap:
                        remap[v] = len(out["pos"]) // 3
                        out["pos"] += pos[v * 3:v * 3 + 3]
                        out["nrm"] += mesh["nrm"][v * 3:v * 3 + 3]
                        out["uv"] += mesh["uv"][v * 2:v * 2 + 2]
                    idx.append(remap[v])
            out["subs"].append({"idx": idx, "mat": sub["mat"]})
        halves.append(out)
    meshes[node["mesh"]] = halves[0]
    meshes.append(halves[1])
    nodes.append(dict(node, name=f"{name}_B", mesh=len(meshes) - 1))
    node["name"] = f"{name}_A"
    print(f"split {name} across axis {axis} at {mid:.3f}")


def main(src, dst, split=()):
    gltf, binary = read_glb(src)
    os.makedirs(dst, exist_ok=True)

    images = []
    for k, img in enumerate(gltf.get("images", [])):
        name = f"tex_{k}.png"
        if "bufferView" in img:
            v = gltf["bufferViews"][img["bufferView"]]
            blob = binary[v.get("byteOffset", 0): v.get("byteOffset", 0) + v["byteLength"]]
        else:
            blob = open(os.path.join(os.path.dirname(src), img["uri"]), "rb").read()
        open(os.path.join(dst, name), "wb").write(blob)
        images.append(name)

    textures = gltf.get("textures", [])
    materials = []
    for m in gltf.get("materials", []):
        pbr = m.get("pbrMetallicRoughness", {})
        tex = pbr.get("baseColorTexture", {}).get("index")
        materials.append({
            "name": m.get("name", "mat"),
            "color": pbr.get("baseColorFactor", [1, 1, 1, 1]),
            "metal": pbr.get("metallicFactor", 1.0),
            "rough": pbr.get("roughnessFactor", 1.0),
            "tex": textures[tex]["source"] if tex is not None else -1,
            "emissive": m.get("emissiveFactor", [0, 0, 0]),
        })

    meshes = []
    for m in gltf["meshes"]:
        pos, nrm, uv, subs = [], [], [], []
        for prim in m["primitives"]:
            at = prim["attributes"]
            base = len(pos) // 3
            p = accessor(gltf, binary, at["POSITION"])
            count = len(p) // 3
            pos += mirror_x(p, 3)
            nrm += mirror_x(accessor(gltf, binary, at["NORMAL"]), 3) if "NORMAL" in at else [0.0] * (count * 3)
            if "TEXCOORD_0" in at:
                t = accessor(gltf, binary, at["TEXCOORD_0"])
                t[1::2] = [1.0 - v for v in t[1::2]]  # glTF V runs top-down
                uv += t
            else:
                uv += [0.0] * (count * 2)
            idx = accessor(gltf, binary, prim["indices"]) if "indices" in prim else list(range(count))
            idx = [int(v) + base for v in idx]
            for k in range(0, len(idx), 3):  # mirroring X flips handedness, so flip winding back
                idx[k + 1], idx[k + 2] = idx[k + 2], idx[k + 1]
            subs.append({"idx": idx, "mat": prim.get("material", -1)})
        meshes.append({"name": m.get("name", "mesh"), "pos": pos, "nrm": nrm, "uv": uv, "subs": subs})

    parent = {}
    for i, n in enumerate(gltf["nodes"]):
        for c in n.get("children", []):
            parent[c] = i
    nodes = []
    for i, n in enumerate(gltf["nodes"]):
        assert "matrix" not in n, "matrix transforms not supported; re-export with TRS"
        t = n.get("translation", [0, 0, 0]); r = n.get("rotation", [0, 0, 0, 1]); s = n.get("scale", [1, 1, 1])
        nodes.append({"name": n.get("name", f"node{i}"), "parent": parent.get(i, -1), "mesh": n.get("mesh", -1),
                      "t": [-t[0], t[1], t[2]], "r": [r[0], -r[1], -r[2], r[3]], "s": s})

    for name in split:
        split_halves(nodes, meshes, name)

    json.dump({"nodes": nodes, "meshes": meshes, "materials": materials, "images": images},
              open(os.path.join(dst, "model.json"), "w"))
    print(f"{len(nodes)} nodes, {len(meshes)} meshes, {len(materials)} materials, {len(images)} images -> {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
