"""Compare modded sharedassets0.assets files against stock: which objects were added, changed or removed.

Usage: python assets_diff.py <stock.assets> <mod.assets> [<mod2.assets> ...]
"""
import hashlib, sys, collections
import UnityPy


def index(path):
    env = UnityPy.load(path)
    sf = next(iter(env.files.values()))
    out = {}
    for pid, obj in sf.objects.items():
        raw = obj.get_raw_data()
        name = ""
        try:
            name = getattr(obj.read(), "m_Name", "") or ""
        except Exception:
            pass
        out[pid] = (obj.type.name, name, hashlib.sha1(raw).hexdigest(), len(raw))
    externals = [e.path for e in getattr(sf, "externals", [])]
    return out, externals, sf.unity_version


stock, stock_ext, ver = index(sys.argv[1])
print("stock:", len(stock), "objects, unity", ver, "externals", len(stock_ext))
for mod in sys.argv[2:]:
    m, ext, mver = index(mod)
    added = [p for p in m if p not in stock]
    removed = [p for p in stock if p not in m]
    changed = [p for p in m if p in stock and m[p][2] != stock[p][2]]
    print(f"\n== {mod}\n unity {mver}; externals {len(ext)} (stock {len(stock_ext)}); new externals: {[e for e in ext if e not in stock_ext]}")
    print(f" added {len(added)}, changed {len(changed)}, removed {len(removed)}")
    for label, ids in (("added", added), ("changed", changed), ("removed", removed)):
        c = collections.Counter(m.get(p, stock.get(p))[0] for p in ids)
        print(f"  {label} by type: {dict(c)}")
        for p in ids[:25]:
            t, n, _, size = m.get(p, stock.get(p))
            print(f"    {p:>8} {t:<14} {size:>9} {n}")
