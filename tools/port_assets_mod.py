"""Port a mod that ships a replacement sharedassets0.assets into XML Part Loader files.

Pulls every part table out of the mod's file, keeps rows whose ID is not in the
current game's tables, and writes them as loader XML so the mod runs on top of
the stock assets instead of replacing them.

Usage: python port_assets_mod.py <mod sharedassets0.assets> <tag> <out_dir>
"""
import html, json, os, re, sys
import UnityPy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TR = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S | re.I)
TD = re.compile(r"<t[dh]([^>]*)>(.*?)</t[dh]>", re.S | re.I)
# Table -> file prefix the loader files use.
PREFIX = {"GPU": "AirCooledGPU", "Water Cooled GPU": "WaterCooledGPU", "CPU": "CPU", "Motherboard": "Motherboard",
          "RAM": "RAM", "PSU": "PSU", "Storage": "Storage", "Coolers": "Cooler", "Cases": "Case",
          "Case Fans": "CaseFan", "Monitors": "Monitor", "Keyboards": "Keyboard", "Mice": "Mouse",
          "Headsets": "Headset", "Mousepads": "Mousepad", "Microphones": "Microphone"}


def parse(txt):
    rows = TR.findall(txt)
    clean = lambda s: html.unescape(re.sub("<[^>]+>", "", s)).strip()
    header = [clean(c[1]) for c in TD.findall(rows[0])]
    out = []
    for r in rows[1:]:
        cells = [clean(c[1]) for c in TD.findall(r)]
        if len(cells) == len(header):
            out.append(dict(zip(header, cells)))
    return header, out


STOP = {"geforce", "radeon", "amd", "nvidia", "intel", "oc", "gaming", "the", "edition", "graphics", "card"}


def tokens(s):
    """Name tokens for duplicate checks; also splits '9070XT' style names into '9070', 'xt'."""
    s = re.sub(r"\b\d+\s*gb\b", " ", s.lower()).replace("gaming pro", "gamingpro")
    s = re.sub(r"(\d)([a-z])", r"\1 \2", s)
    return frozenset(t for t in re.findall(r"[a-z0-9+]+", s) if t not in STOP)


def existing_names(stock):
    """(maker, tokens) for every stock part and every MegaParts / already-ported XML."""
    names = {(r["Manufacturer"].lower(), tokens(r["Part Name"])) for d in stock.values() for r in d["rows"]}
    for folder in (os.path.join(ROOT, "out", "mods"), sys.argv[3]):
        for f in os.listdir(folder) if os.path.isdir(folder) else []:
            cells = dict(re.findall(r'<td div="(Manufacturer|Part Name)">(.*?)</td>', open(os.path.join(folder, f), encoding="utf-8").read()))
            if cells:
                names.add((cells.get("Manufacturer", "").lower(), tokens(html.unescape(cells.get("Part Name", "")))))
    return names


def catalog_has(key, _cache={}):
    """True if the game's Addressables catalog contains this prefab key."""
    if "blob" not in _cache:
        _cache["blob"] = open(os.path.join(GAME, "PCBS2_Data", "StreamingAssets", "aa", "catalog.bin"), "rb").read()
    return key.encode("utf-8") in _cache["blob"]


GAME = r"E:\Games\PC.Building.Simulator.2.v1.17.02"


def main(mod_path, tag, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    stock = {n: json.load(open(os.path.join(ROOT, "data", n + ".json"), encoding="utf-8")) for n in PREFIX
             if os.path.exists(os.path.join(ROOT, "data", n + ".json"))}
    stock_ids = {r["ID"] for d in stock.values() for r in d["rows"]}
    known = existing_names(stock)
    env = UnityPy.load(mod_path)
    report = []
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        d = obj.read()
        if d.m_Name not in stock:
            continue
        txt = d.m_Script if isinstance(d.m_Script, str) else bytes(d.m_Script).decode("utf-8", "replace")
        header, rows = parse(txt)
        cur_header = stock[d.m_Name]["header"]
        new = [r for r in rows if r.get("ID") and r["ID"] not in stock_ids and r.get("Class") != "Dummy"]
        for r in new:
            key = (r["Manufacturer"].lower(), tokens(r["Part Name"]))
            if key in known or "do not turn on" in r["Part Name"].lower():
                report.append((d.m_Name, r["ID"], r["Manufacturer"], r["Part Name"], "skipped: already in game/MegaParts", 0))
                continue
            known.add(key)
            # Old-format rows: drop columns the current game no longer has, blank the ones it added.
            row = {c: r.get(c, "") for c in cur_header}
            row["Notes"] = f"Ported from {tag}"
            if not catalog_has(row["Asset Path"].rsplit("/", 1)[-1]):
                # Model gone from this game version: borrow one from a stock part on the same socket/chipset.
                same = [s for s in stock[d.m_Name]["rows"] if s["Asset Path"] and catalog_has(s["Asset Path"].rsplit("/", 1)[-1])
                        and all(s.get(k) == row.get(k) for k in ("CPU Socket", "Chipset") if row.get(k))]
                if same:
                    row["Asset Path"] = same[0]["Asset Path"]
            title = f"{PREFIX[d.m_Name]}_{row['Manufacturer']} {row['Part Name']}"
            fn = re.sub(r'[<>:"/\\|?*]', "-", f"{tag}_{title}").strip() + ".xml"
            lines = [title, "<table>", "\t<tr>"]
            lines += [f'\t\t<td div="{html.escape(c)}">{html.escape(row[c], quote=False)}</td>' for c in cur_header]
            lines += ["\t</tr>", "</table>"]
            with open(os.path.join(out_dir, fn), "w", encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(lines) + "\n")
            missing = [c for c in cur_header if c and c not in r]
            report.append((d.m_Name, row["ID"], row["Manufacturer"], row["Part Name"],
                           "ok" if catalog_has(row["Asset Path"].rsplit("/", 1)[-1]) else "UNKNOWN ASSET " + row["Asset Path"],
                           len(missing)))
    for line in report:
        print(*line, sep=" | ")
    ported = [r for r in report if not r[4].startswith("skipped")]
    print(f"{tag}: {len(ported)} ported, {len(report) - len(ported)} skipped as duplicates, "
          f"{sum(1 for r in ported if r[4] != 'ok')} with unknown asset paths")


if __name__ == "__main__":
    main(*sys.argv[1:4])
