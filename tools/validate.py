"""Check generated XML files: parse, column set, unique IDs, numeric fields, asset paths exist in stock."""
import html, json, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "out", "mods")
TD = re.compile(r'<td div="([^"]*)">(.*?)</td>', re.S)
NUMERIC = ["Price", "SellPrice", "Level", "Wattage", "Frequency", "Cores", "Threads", "VRAM (GB)", "Size (GB)",
           "Total Size (GB)", "Base Core Clock Freq", "Single GPU Graphics Score", "Basic CPU Score (TS)", "Air Flow"]

tables = {}
for f in os.listdir(os.path.join(ROOT, "data")):
    d = json.load(open(os.path.join(ROOT, "data", f), encoding="utf-8"))
    tables[f[:-5]] = d
# Part Type -> table; "GPU" is shared by the air and water tables, so tell those apart by file prefix.
TYPE_TABLE = {r["Part Type"]: n for n, d in tables.items() for r in d["rows"] if n != "Water Cooled GPU"}
stock_ids ={r["ID"] for d in tables.values() for r in d["rows"]}
stock_assets = {r["Asset Path"] for d in tables.values() for r in d["rows"]}

errors, ids, counts = [], {}, collections.Counter()
for fn in sorted(os.listdir(MODS)):
    text = open(os.path.join(MODS, fn), encoding="utf-8").read()
    rows = [dict((k, html.unescape(v)) for k, v in TD.findall(tr)) for tr in re.findall(r"<tr>(.*?)</tr>", text, re.S)]
    if not rows:
        errors.append(f"{fn}: no rows"); continue
    r = rows[0]
    table = "Water Cooled GPU" if fn.startswith("WaterCooledGPU_") else TYPE_TABLE.get(r.get("Part Type", ""))
    if not table:
        errors.append(f"{fn}: unknown Part Type {r.get('Part Type')}"); continue
    counts[table] += 1
    header = [h for h in tables[table]["header"]]
    for row in rows:
        if list(row.keys()) != header:
            errors.append(f"{fn}: columns differ from stock {table} header")
        for k in NUMERIC:
            if k in row and row[k] != "":
                try:
                    float(row[k])
                except ValueError:
                    errors.append(f"{fn}: {k}={row[k]!r} not numeric")
        if row["Asset Path"] not in stock_assets:
            errors.append(f"{fn}: unknown asset {row['Asset Path']}")
        if float(row["Price"]) <= 0:
            errors.append(f"{fn}: bad price")
    pid = r["ID"]
    if pid in stock_ids:
        errors.append(f"{fn}: ID {pid} clashes with stock")
    if pid in ids:
        errors.append(f"{fn}: ID {pid} duplicates {ids[pid]}")
    ids[pid] = fn
print("files:", sum(counts.values()), dict(counts))
print("errors:", len(errors))
for e in errors[:40]:
    print("  ", e)
sys.exit(1 if errors else 0)
