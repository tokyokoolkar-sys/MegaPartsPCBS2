"""Build a merged sharedassets0.assets: the current game's file plus the part rows that
replacement-sharedassets mods add.

The mods were built against an older game version, so dropping their file in replaces
newer stock tables with old ones. This keeps the stock file and appends only the
mods' new rows (converted to the current column layout). The stock file is backed
up once as sharedassets0.assets.stock and is always the merge source, so this can be
re-run. Mod files are read, never changed.

Rows are skipped when their ID is already in the game, or already supplied by an XML
file in <game>/mods (e.g. a mod that ships both an assets file and an XML pack).

Usage: python merge_assets.py [--restore]
"""
import html, os, re, shutil, sys
import UnityPy

GAME = r"E:\Games\PC.Building.Simulator.2.v1.17.02"
REF = r"E:\Games\PCBS2-mods-ref"
MODS = {  # tag -> replacement sharedassets0.assets
    "Corfunj Expansion": os.path.join(REF, "Corfunj Expansion Mod FILE-112-0-0-5-1764771222", "sharedassets0.assets"),
    "New Parts 3D": os.path.join(REF, "New Parts 3D", "sharedassets0.assets"),
}
TARGET = os.path.join(GAME, "PCBS2_Data", "sharedassets0.assets")
BACKUP = TARGET + ".stock"
TR = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S | re.I)
TD = re.compile(r"<t[dh]([^>]*)>(.*?)</t[dh]>", re.S | re.I)
clean = lambda s: html.unescape(re.sub("<[^>]+>", "", s)).strip()


def text(d):
    return d.m_Script if isinstance(d.m_Script, str) else bytes(d.m_Script).decode("utf-8", "replace")


def parse(txt):
    rows = TR.findall(txt)
    if not rows:
        return None, []
    header = [clean(c[1]) for c in TD.findall(rows[0])]
    out = []
    for r in rows[1:]:
        tds = TD.findall(r)
        if not tds:
            continue
        names = [m.group(1) if (m := re.search(r'div="([^"]*)"', a)) else None for a, _ in tds]
        if all(n is not None for n in names):  # cells carry their column name: map by name (some mod rows are short a few cells)
            out.append({n: clean(v) for n, (_, v) in zip(names, tds)})
        elif len(tds) == len(header):
            out.append(dict(zip(header, [clean(v) for _, v in tds])))
    return header, out


def xml_ids():
    ids = set()
    for f in os.listdir(os.path.join(GAME, "mods")):
        if f.endswith(".xml"):
            m = re.search(r'<td div="ID">(.*?)</td>', open(os.path.join(GAME, "mods", f), encoding="utf-8", errors="replace").read())
            if m:
                ids.add(m.group(1).strip())
    return ids


def main():
    if "--restore" in sys.argv:
        shutil.copy2(BACKUP, TARGET)
        print("Restored stock sharedassets0.assets")
        return
    if not os.path.exists(BACKUP):
        shutil.copy2(TARGET, BACKUP)
    catalog = open(os.path.join(GAME, "PCBS2_Data", "StreamingAssets", "aa", "catalog.bin"), "rb").read()
    has_model = lambda p: bool(p) and p.rsplit("/", 1)[-1].encode("utf-8") in catalog

    env = UnityPy.load(BACKUP)
    stock = {}
    for obj in env.objects:
        if obj.type.name == "TextAsset":
            d = obj.read()
            h, rows = parse(text(d))
            if h and "ID" in h:
                stock[d.m_Name] = (obj, d, h, rows)
    taken = {r.get("ID") for _, _, _, rows in stock.values() for r in rows} | xml_ids()

    added = {}
    for tag, path in MODS.items():
        for obj in UnityPy.load(path).objects:
            if obj.type.name != "TextAsset":
                continue
            d = obj.read()
            if d.m_Name not in stock:
                continue
            _, rows = parse(text(d))
            _, _, cur_h, cur_rows = stock[d.m_Name]
            for r in rows:
                if not r.get("ID") or r["ID"] in taken or r.get("Class") == "Dummy" or "do not turn on" in r.get("Part Name", "").lower():
                    continue
                taken.add(r["ID"])
                row = {c: r.get(c, "") for c in cur_h}
                note = ""
                if not has_model(row.get("Asset Path")):
                    # Model gone from this game version: borrow one from a stock part on the same socket/chipset.
                    same = [s for s in cur_rows if has_model(s.get("Asset Path"))
                            and all(s.get(k) == row.get(k) for k in ("CPU Socket", "Chipset") if row.get(k))]
                    if same:
                        note = f" (model {row['Asset Path']} missing, using {same[0]['Asset Path']})"
                        row["Asset Path"] = same[0]["Asset Path"]
                    else:
                        note = " (NO MODEL FOUND)"
                added.setdefault(d.m_Name, []).append(row)
                print(f"{tag} | {d.m_Name} | {row['ID']} | {row['Manufacturer']} {row['Part Name']}{note}")

    for name, rows in added.items():
        _, d, h, _ = stock[name]
        block = "".join("\t<tr>\r\n" + "".join(f'\t\t<td div="{html.escape(c)}">{html.escape(r[c], quote=False)}</td>\r\n'
                                                for c in r) + "\t</tr>\r\n" for r in rows)
        t = text(d)
        i = t.rfind("</table>")
        d.m_Script = t[:i] + block + t[i:]
        d.save()
    with open(TARGET, "wb") as fh:
        fh.write(env.file.save())
    print(f"Merged {sum(map(len, added.values()))} rows into {TARGET} (stock backup: {BACKUP})")


if __name__ == "__main__":
    main()
