# Scan game asset files for TextAssets that look like part tables; dump them.
import sys, os, UnityPy

data = sys.argv[1]
out = sys.argv[2]
os.makedirs(out, exist_ok=True)
files = [os.path.join(data, f) for f in os.listdir(data)
         if f.endswith(".assets") or f.startswith("level")]
for f in files:
    try:
        env = UnityPy.load(f)
    except Exception as e:
        print("skip", f, e); continue
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        d = obj.read()
        txt = d.m_Script if isinstance(d.m_Script, str) else bytes(d.m_Script).decode("utf-8", "replace")
        name = d.m_Name
        tag = "TABLE" if "<td" in txt[:20000] else ""
        print(f"{os.path.basename(f)}\t{name}\t{len(txt)}\t{tag}")
        if tag:
            with open(os.path.join(out, name + ".html"), "w", encoding="utf-8") as fh:
                fh.write(txt)
