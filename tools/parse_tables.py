# Parse the game's HTML part tables into JSON lists of {column: value} rows.
import sys, os, re, json, html

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
TR = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S | re.I)
TD = re.compile(r"<t[dh]([^>]*)>(.*?)</t[dh]>", re.S | re.I)
DIV = re.compile(r'div="([^"]*)"')

for name in ["CPU", "GPU", "Water Cooled GPU", "Motherboard", "RAM", "PSU", "Storage", "Coolers", "Cases", "Case Fans", "Monitors", "Keyboards", "Mice", "Headsets", "Mousepads", "Microphones"]:
    txt = open(os.path.join(src, name + ".html"), encoding="utf-8").read()
    rows = TR.findall(txt)
    header = [html.unescape(re.sub("<[^>]+>", "", c[1])).strip() for c in TD.findall(rows[0])]
    recs = []
    for r in rows[1:]:
        cells = [html.unescape(re.sub("<[^>]+>", "", c[1])).strip() for c in TD.findall(r)]
        if len(cells) != len(header):
            continue
        recs.append(dict(zip(header, cells)))
    json.dump({"header": header, "rows": recs}, open(os.path.join(out, name + ".json"), "w", encoding="utf-8"), indent=1)
    print(name, len(header), "cols", len(recs), "rows")


