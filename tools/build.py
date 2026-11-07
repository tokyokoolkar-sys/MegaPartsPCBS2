"""Generate PCBS2 XML Part Loader files from catalog.py.

Each part clones a stock game row (data/*.json, extracted from sharedassets0)
of the same kind, so benchmark lookups, prefab paths and the many columns we
don't touch stay valid. Usage: python build.py [out_dir]
"""
import csv, hashlib, html, json, math, os, re, sys

import catalog as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "out", "mods")
NOTE = "PCBS2 MegaParts"


def load(name):
    d = json.load(open(os.path.join(DATA, name + ".json"), encoding="utf-8"))
    return d["header"], d["rows"]


TABLES = {n: load(n) for n in ["GPU", "Water Cooled GPU", "CPU", "Motherboard", "RAM", "Storage", "PSU", "Coolers",
                               "Cases", "Case Fans", *C.PERIPHERALS]}


def usable(rows):
    return [r for r in rows if r["Class"] not in ("Dummy", "TIC") and r["Asset Path"] and not r["ID"].startswith("DUMMY")]


STOCK = {n: usable(rows) for n, (_, rows) in TABLES.items()}
STOCK_IDS = {r["ID"] for _, rows in TABLES.values() for r in rows}


def num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def fmt(x):
    """Integers without '.0', floats trimmed."""
    if isinstance(x, float):
        return str(int(round(x))) if abs(x - round(x)) < 1e-9 else f"{x:.4f}".rstrip("0").rstrip(".")
    return str(x)


STOP = {"geforce", "radeon", "amd", "nvidia", "intel", "oc", "gaming", "the", "edition", "graphics", "card"}


def tokens(s):
    return {t for t in re.findall(r"[a-z0-9+]+", s.lower()) if t not in STOP and not re.fullmatch(r"\d+gb", t)}


def duplicate_of(table, mfr, name, extra=lambda r: True):
    """Stock row with the same maker whose name tokens match ours, if any."""
    want = tokens(name)
    for r in TABLES[table][1]:
        if r["Manufacturer"].lower() == mfr.lower() and extra(r):
            have = tokens(r["Part Name"])
            if want == have or (len(want) >= 3 and want <= have):
                return r
    return None


def best(rows, score) -> dict:
    """Highest-scoring row; raises if there are none."""
    return max(rows, key=score)


def best_or(rows, score, default):
    rows = list(rows)
    return max(rows, key=score) if rows else default


# ------------------------------------------------------------------ output
built, skipped, ids = [], [], set()


def make_id(tmpl_id, key, prefix=None):
    if prefix is None:
        m = re.match(r"(.+?)_[A-Za-z0-9.!-]+_\d+$", tmpl_id)
        prefix = m.group(1) if m else tmpl_id.split("_")[0]
    pid = f"{prefix}_MegaParts_{hashlib.sha1(key.encode()).hexdigest()[:8]}"
    assert pid not in STOCK_IDS, pid
    return pid


def emit(table, file_prefix, tmpl, mfr, name, price, fields, concat_suffix="", new_id=None, extra_rows=()):
    """Clone tmpl, apply common + given fields, register the part (one or more rows)."""
    header = TABLES[table][0]
    pid = new_id or make_id(tmpl["ID"], f"{table}|{mfr}|{name}|{concat_suffix}")
    if pid in ids and not new_id:
        skipped.append((table, mfr, name, "id collision")); return
    ids.add(pid)
    rows = []
    for t in (tmpl, *extra_rows):
        r = dict(t)
        ratio = num(t["SellPrice"]) / num(t["Price"], 1) if num(t["Price"]) else 0.5
        r.update({"Manufacturer": mfr, "ID": pid, "Part Name": name, "In Game": "Yes", "Imported to Game": "Yes",
                  "Working in game": "Yes", "In Shop": "Yes", "Use in Random Jobs": "Yes", "Headline": "",
                  "Price": fmt(float(round(price))), "SellPrice": fmt(float(max(1, round(price * ratio)))),
                  "Product Page": "", "Notes": NOTE})
        if "Icon Path" in r:
            r["Icon Path"] = ""
        extra = fields(t) if callable(fields) else fields
        r.update({k: fmt(v) if isinstance(v, (int, float)) else v for k, v in extra.items()})
        r["Concat name"] = f"({r['Level']}) {mfr} {name}{concat_suffix}"
        rows.append(r)
    title = f"{file_prefix}_{mfr} {name}{concat_suffix}"
    built.append({"table": table, "title": title, "header": header, "rows": rows, "tmpl": tmpl["ID"],
                  "asset": rows[0]["Asset Path"], "price": rows[0]["Price"]})


def write_all():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".xml"):
            os.remove(os.path.join(OUT, f))
    seen = set()
    for b in built:
        fn = re.sub(r'[<>:"/\\|?*]', "-", b["title"]).strip()
        while fn.lower() in seen:
            fn += "_"
        seen.add(fn.lower())
        lines = [b["title"], "<table>"]
        for r in b["rows"]:
            lines.append("\t<tr>")
            for col in b["header"]:
                lines.append(f'\t\t<td div="{html.escape(col)}">{html.escape(r.get(col, ""), quote=False)}</td>')
            lines.append("\t</tr>")
        lines.append("</table>")
        with open(os.path.join(OUT, fn + ".xml"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines) + "\n")
        b["file"] = fn + ".xml"


# ------------------------------------------------------------------ GPUs
LINE_KEYS = ["tuf", "strix", "astral", "dual", "prime", "ventus", "suprim", "trio", "slim", "windforce", "eagle",
             "aero", "aorus", "twin", "trinity", "solid", "amp", "verto", "xlr8", "gamingpro", "gamerock", "ghost",
             "phoenix", "pulse", "pure", "nitro", "fighter", "hellhound", "reaper", "devil", "swft", "merc", "qick",
             "quicksilver", "mercury", "challenger", "steel", "phantom", "taichi", "titan", "bifrost", "photon"]
TIER = {0: (1.00, 1.00), 1: (1.02, 1.07), 2: (1.04, 1.18)}
GPU_MODEL_FIELDS = ["Asset Path", "Length", "Slot Size", "Display Width", "Width", "Display Depth", "Depth",
                    "Component Lighting", "Player Lighting Control", "Power Splitter", "Rigid SLI Bridge Model"]


def gpu_family(chip):
    m = re.search(r"(RTX|RX|Arc)\s*([A-Z]?)(\d)", chip)
    return (m.group(1), m.group(2), m.group(3)) if m else (chip,)


def build_gpus():
    rows = STOCK["GPU"]
    for mfr, line, tier, chips in C.GPU_LINES:
        key = next((k for k in LINE_KEYS if k in line.lower().replace("-", "")), None)
        for chip in chips:
            base_chip, perf = C.CHIPSET_FALLBACK.get(chip, (chip, 1.0))
            same = [r for r in rows if r["Chipset"] == base_chip]
            if not same:
                skipped.append(("GPU", mfr, line.format(c=chip), "no stock chipset")); continue
            for vram in C.VRAM_VARIANTS.get(chip, [None]):
                tmpl = best(same, lambda r: (r["Manufacturer"] in ("NVIDIA", "AMD", "Intel")) * 4 +
                            (vram is not None and num(r["VRAM (GB)"]) == vram) * 8)
                gb = int(vram or num(tmpl["VRAM (GB)"]))
                name = f"{line.format(c=C.DISPLAY.get(chip, chip))} {gb}GB"
                if duplicate_of("GPU", mfr, name, lambda r: r["Chipset"] == base_chip and num(r["VRAM (GB)"]) == gb):
                    skipped.append(("GPU", mfr, name, "already in game")); continue
                donor = best_or((r for r in rows if r["Manufacturer"].lower() == mfr.lower()),
                                lambda r: bool(key and key in r["Part Name"].lower().replace(" ", "").replace("-", "")) * 10 +
                                (gpu_family(r["Chipset"]) == gpu_family(chip)) * 3 - abs(num(r["Length"]) - num(tmpl["Length"])) / 100,
                                tmpl)
                cf, pf = TIER[tier]
                pf *= perf

                def fields(t, donor=donor, cf=cf, gb=gb, perf=perf):
                    f = {k: donor[k] for k in GPU_MODEL_FIELDS if k in donor}
                    f["VRAM (GB)"] = gb
                    for k in ("Base Core Clock Freq", "UL Observed GPU Clocks", "GPU max clock"):
                        if num(t.get(k)):
                            f[k] = round(num(t[k]) * cf)
                    for k in ("Single GPU Graphics Score", "Double GPU Graphics Score", "Triple GPU Graphics Score",
                              "Quad GPU Graphics Score", "OC Single GPU score", "OC Double GPU score"):
                        if num(t.get(k)):
                            f[k] = round(num(t[k]) * cf ** 0.8 * perf)
                    return f
                vram_pf = 1.12 if vram and vram > num(tmpl["VRAM (GB)"]) else (0.9 if vram and vram < num(tmpl["VRAM (GB)"]) else 1)
                emit("GPU", "AirCooledGPU", tmpl, mfr, name, num(tmpl["Price"]) * pf * vram_pf, fields)


def reference_gpu(chip):
    """The vendor reference (Founders/AMD/Intel) stock row for a chipset."""
    return best((r for r in STOCK["GPU"] if r["Chipset"] == chip),
                lambda r: (r["Manufacturer"] in ("NVIDIA", "AMD", "Intel")) * 4)


GPU_SCORES = ("Single GPU Graphics Score", "Double GPU Graphics Score", "Triple GPU Graphics Score",
              "Quad GPU Graphics Score", "OC Single GPU score", "OC Double GPU score")


def build_pro_gpus():
    for mfr, name, chip, perf, vram, watts, pf in C.PRO_GPUS:
        full = f"{name} {vram}GB"
        if duplicate_of("GPU", mfr, full):
            skipped.append(("GPU", mfr, full, "already in game")); continue
        tmpl = reference_gpu(chip)
        fields = {"VRAM (GB)": vram, "Wattage": watts,
                  **{k: round(num(tmpl[k]) * perf) for k in GPU_SCORES if num(tmpl.get(k))}}
        emit("GPU", "AirCooledGPU", tmpl, mfr, full, num(tmpl["Price"]) * pf, fields)


# Columns that describe the liquid-cooled card's physical model; everything else comes from the air chipset.
WC_MODEL_FIELDS = {"Part Type", "Class", "Asset Path", "Length", "Slot Size", "Real Width", "Width", "Component Lighting",
                   "Player Lighting Control", "Rigid SLI Bridge Model", "Power Splitter", "Boost Multiplier",
                   "Score increase", "Model Supplied", "Licensor Approved", "Is Scale V2",
                   # identity columns, set by emit()
                   "ID", "Manufacturer", "Part Name", "Price", "SellPrice", "Concat name", "Notes", "Product Page"}


def build_water_gpus():
    rows = STOCK["Water Cooled GPU"]
    for mfr, name, chip, vram, pf in C.WATER_GPUS:
        full = f"{name} {vram}GB"
        if duplicate_of("Water Cooled GPU", mfr, full):
            skipped.append(("Water Cooled GPU", mfr, full, "already in game")); continue
        air = reference_gpu(chip)
        tmpl = best(rows, lambda r: (r["Manufacturer"].lower() == mfr.lower()) * 5 +
                    (gpu_family(r["Chipset"]) == gpu_family(chip)) * 3 + ("RTX" in r["Chipset"]) * ("RTX" in chip) * 2)

        def fields(t, air=air, vram=vram):
            f = {k: air[k] for k in t if k in air and k not in WC_MODEL_FIELDS}
            f.update({"VRAM (GB)": vram, "Normal GPU max clock": air["GPU max clock"],
                      "Normal GPU Max mem clock": air["GPU max mem clock"]})
            for k in ("Base Core Clock Freq", "UL Observed GPU Clocks", "GPU max clock"):
                if num(air.get(k)):
                    f[k] = round(num(air[k]) * 1.04)
            for k in GPU_SCORES:
                if k in t and num(air.get(k)):
                    f[k] = round(num(air[k]) * 1.03)
            return f
        emit("Water Cooled GPU", "WaterCooledGPU", tmpl, mfr, full, num(air["Price"]) * pf, fields)


# ------------------------------------------------------------------ CPUs
def build_cpus():
    rows = STOCK["CPU"]
    for name, mfr, tname, freq, cores, ecores, threads, watts, unlocked, pf in C.CPUS:
        tmpls = [r for r in rows if r["Part Name"] == tname]
        if not tmpls:
            skipped.append(("CPU", mfr, name, f"template {tname} missing")); continue
        if duplicate_of("CPU", mfr, name, lambda r: r["Part Name"].lower() == name.lower()):
            skipped.append(("CPU", mfr, name, "already in game")); continue
        t0 = tmpls[0]
        pid = make_id(t0["ID"], f"CPU|{mfr}|{name}")

        def fields(t):
            fr = freq / num(t["Frequency"], freq)
            ce = (cores - 0.5 * ecores) / max(1, num(t["Cores"]) - 0.5 * num(t["Efficiency Cores"]))
            s = fr * ce ** 0.75
            f = {"Frequency": freq, "Cores": cores, "Efficiency Cores": ecores, "Threads": threads, "Wattage": watts,
                 "Can Overclock": "Yes" if unlocked else "No",
                 "Max Freq": round(num(t["Max Freq"], freq) * fr) if unlocked else freq,
                 "Price": round(num(t["Price"]) * pf),
                 "SellPrice": round(num(t["SellPrice"]) * pf)}
            for k in ("Basic CPU Score (TS)", "Basic CPU Score (TSX)", "Overclock Basic CPU Score"):
                if num(t.get(k)):
                    f[k] = round(num(t[k]) * s)
            if not unlocked:
                f["Overclock Basic CPU Score"] = f.get("Basic CPU Score (TS)", t.get("Overclock Basic CPU Score"))
            return f
        emit("CPU", "CPU", t0, mfr, name, num(t0["Price"]) * pf, fields, new_id=pid, extra_rows=tmpls[1:])


# ------------------------------------------------------------------ Motherboards
def build_motherboards():
    rows = STOCK["Motherboard"]
    chipsets = {}
    for r in rows:
        chipsets.setdefault(r["CPU Socket"], set()).add(r["Chipset"])
    for mfr, name, socket, chipset, size, ram, price in C.MOTHERBOARDS:
        if duplicate_of("Motherboard", mfr, name):
            skipped.append(("Motherboard", mfr, name, "already in game")); continue
        tmpl = best(rows, lambda r: (r["Motherboard Size"] == size) * 20 + (r["CPU Socket"] == socket) * 10 +
                    (r["Ram Type"] == ram) * 4 + (r["Manufacturer"].lower() == mfr.lower()) * 5 +
                    (r["Chipset"] == chipset) * 2)
        mem = best_or((r for r in rows if r["CPU Socket"] == socket and r["Ram Type"] == ram),
                      lambda r: num(r["Max Memory Speed"]), None)
        if mem is None:
            mem = best((r for r in rows if r["Ram Type"] == ram), lambda r: num(r["Max Memory Speed"]))
        same_socket = best((r for r in rows if r["CPU Socket"] == socket), lambda r: r["Chipset"] == chipset)
        fields = {"CPU Socket": socket, "Ram Type": ram, "Motherboard Size": tmpl["Motherboard Size"],
                  "Chipset": chipset if chipset in chipsets.get(socket, ()) else same_socket["Chipset"],
                  "Default Memory Speed": mem["Default Memory Speed"], "Memory Speed Steps": mem["Memory Speed Steps"],
                  "Max Memory Speed": mem["Max Memory Speed"],
                  "Can Overclock": "No" if chipset in C.LOCKED_CHIPSETS else "Yes", "Level": same_socket["Level"]}
        emit("Motherboard", f"Motherboard_{size}", tmpl, mfr, name, price, fields)


# ------------------------------------------------------------------ RAM
def build_ram():
    rows = STOCK["RAM"]
    for mfr, line, rtype, freq, cas, volts, sizes, light, tier in C.RAM:
        for size in sizes:
            suffix = f" {size}GB (1x {size}GB) {freq}"
            if duplicate_of("RAM", mfr, line, lambda r: num(r["Total Size (GB)"]) == size and num(r["Frequency"]) == freq):
                skipped.append(("RAM", mfr, line + suffix, "already in game")); continue
            tmpl = best((r for r in rows if r["Ram Type"] == rtype),
                        lambda r: ((r["Component Lighting"] != "N/A") == (light != "N/A")) * 6 +
                        (r["Manufacturer"].lower() == mfr.lower()) * 5 + (num(r["Size each (GB)"]) == size) * 2 -
                        abs(num(r["Frequency"]) - freq) / 1000)
            base = 3.0 + 0.4 * (freq - 5600) / 400 if rtype == "DDR5" else 2.5 + 0.3 * (freq - 3200) / 400
            ppg = round(base * tier * (1.1 if light != "N/A" else 1.0), 2)
            tcas = num(tmpl["Factory Timings"].split("-")[0], cas)
            fields = {"Total Size (GB)": size, "Size each (GB)": size, "Number": 1, "Frequency": freq, "Voltage": f"{volts:.2f}",
                      "Factory Timings": f"{cas}-{round(cas * 1.2)}-{round(cas * 1.2)}-{round(cas * 2.5)}",
                      "Ideal CAS Latency": max(10, round(num(tmpl["Ideal CAS Latency"], cas) * cas / tcas)),
                      "Max Speed": max(num(tmpl["Max Speed"]), freq + 400), "Price per gig": ppg}
            emit("RAM", "RAM", tmpl, mfr, line, ppg * size, fields, concat_suffix=suffix)


# ------------------------------------------------------------------ Storage
def cap_label(gb):
    return f"{gb // 1000}TB" if gb >= 1000 and gb % 1000 == 0 else f"{gb}GB"


def build_storage():
    rows = STOCK["Storage"]
    for mfr, line, ptype, speed, sizes, per_tb, sink in C.STORAGE:
        for gb in sizes:
            name = f"{line} {cap_label(gb)}"
            if duplicate_of("Storage", mfr, name, lambda r: num(r["Size (GB)"]) == gb):
                skipped.append(("Storage", mfr, name, "already in game")); continue
            tmpl = best_or((r for r in rows if r["Part Type"] == ptype),
                           lambda r: ((r["Includes Heatsink"] == "Yes") == sink) * 6 + (r["Manufacturer"].lower() == mfr.lower()) * 5,
                           None)
            if tmpl is None:
                skipped.append(("Storage", mfr, name, f"no stock {ptype}")); continue
            fields = {"Size (GB)": gb, "Speed": speed if ptype != "HDD" else tmpl["Speed"] or speed}
            prefix = {"M2": "Storage_M.2", "SSD": "Storage_SSD", "HDD": "Storage_HDD"}[ptype]
            emit("Storage", prefix, tmpl, mfr, name, max(25, per_tb * gb / 1000 + 15), fields)


# ------------------------------------------------------------------ PSUs
def build_psus():
    rows = STOCK["PSU"]
    for mfr, name, watts, size, modular, price in C.PSUS:
        if duplicate_of("PSU", mfr, name):
            skipped.append(("PSU", mfr, name, "already in game")); continue
        tmpl = best((r for r in rows if r["Size"] == size),
                    lambda r: (r["Manufacturer"].lower() == mfr.lower()) * 5 + (r["Modularity"] == modular) * 8 -
                    abs(num(r["Wattage"]) - watts) / 500)
        emit("PSU", f"PSU_{size}", tmpl, mfr, name, price, {"Wattage": watts, "Modularity": tmpl["Modularity"]})


# ------------------------------------------------------------------ Coolers
MODERN_SOCKETS = ["AM4", "AM5", "LGA 1200", "LGA 1700", "LGA 1851"]


def socket_fields(t):
    f = {s: "1" for s in MODERN_SOCKETS}
    have = [s.strip() for s in t["CPU Socket List"].split(",") if s.strip()]
    f["CPU Socket List"] = ", ".join(dict.fromkeys(have + MODERN_SOCKETS)) + ","
    return f


def build_coolers():
    rows = STOCK["Coolers"]
    for mfr, name, height, price, light in C.AIR_COOLERS:
        if duplicate_of("Coolers", mfr, name):
            skipped.append(("Coolers", mfr, name, "already in game")); continue
        tmpl = best((r for r in rows if r["Part Type"] == "Air Cooler" and r["No Fan"] != "Yes"),
                    lambda r: (r["Manufacturer"].lower() == mfr.lower()) * 5 + (r["AM5"] == "1" and r["LGA 1851"] == "1") * 4 +
                    ((r["Component Lighting"] != "N/A") == (light != "N/A")) * 3 - abs(num(r["Height"]) - height) / 10)
        emit("Coolers", "AirCooler", tmpl, mfr, name, price, lambda t, h=height: {**socket_fields(t), "Height": h})
    for mfr, name, fan, count, price, light in C.LIQUID_COOLERS:
        if duplicate_of("Coolers", mfr, name):
            skipped.append(("Coolers", mfr, name, "already in game")); continue
        tmpl = best((r for r in rows if r["Part Type"] == "Liquid Cooler"),
                    lambda r: (num(r["Size"]) == fan and num(r["Slots"]) == count) * 20 +
                    (r["Manufacturer"].lower() == mfr.lower()) * 5 + (r["AM5"] == "1" and r["LGA 1851"] == "1") * 4 +
                    ((r["Component Lighting"] != "N/A") == (light != "N/A")) * 3)
        if num(tmpl["Size"]) != fan or num(tmpl["Slots"]) != count:
            skipped.append(("Coolers", mfr, name, f"no stock {fan}x{count} radiator")); continue
        emit("Coolers", "LiquidCooler", tmpl, mfr, name, price, socket_fields)


# ------------------------------------------------------------------ Cases
SIZES = ["Mini-ITX", "Micro-ATX", "S-ATX", "E-ATX"]


def build_cases():
    rows = STOCK["Cases"]
    for mfr, name, board, csize, price in C.CASES:
        if duplicate_of("Cases", mfr, name):
            skipped.append(("Cases", mfr, name, "already in game")); continue
        nxt = SIZES[SIZES.index(board) + 1] if board != "E-ATX" else None

        def score(r):
            fits = r.get(board) == "1" and (nxt is None or r.get(nxt) != "1")
            return fits * 10 + (r["Case Size"] == csize) * 8 + (r["Manufacturer"].lower() == mfr.lower()) * 5 + (r["Is Open Bench"] != "Yes") * 20
        emit("Cases", "Case", best(rows, score), mfr, name, price, {})


# ------------------------------------------------------------------ Case fans
def build_fans():
    rows = STOCK["Case Fans"]
    for mfr, name, size, cfm, pressure, price, light in C.FANS:
        if duplicate_of("Case Fans", mfr, name):
            skipped.append(("Case Fans", mfr, name, "already in game")); continue
        tmpl = best(rows, lambda r: (num(r["Size"]) == size) * 20 + (r["Manufacturer"].lower() == mfr.lower()) * 5 +
                    ((r["Component Lighting"] != "N/A") == (light != "N/A")) * 4)
        emit("Case Fans", "CaseFan", tmpl, mfr, name, price, {"Air Flow": cfm, "Air Pressure": pressure})


# ------------------------------------------------------------------ Peripherals
def build_peripherals():
    for table, parts in C.PERIPHERALS.items():
        rows = STOCK[table]
        prefix = rows[0]["Part Type"]
        for mfr, name, price, extra in parts:
            if duplicate_of(table, mfr, name):
                skipped.append((table, mfr, name, "already in game")); continue
            # Closest price spreads parts across models instead of piling onto one.
            tmpl = best(rows, lambda r: (r["Manufacturer"].lower() == mfr.lower()) * 5 +
                        sum(r.get(k) == v for k, v in extra.items()) * 6 + (r["Manufacturer"] != "DFL") * 2 -
                        abs(math.log(max(num(r["Price"]), 1) / price)))
            pid = make_id(tmpl["ID"], f"{table}|{mfr}|{name}|", prefix=prefix.upper().replace(" ", "_"))
            emit(table, prefix, tmpl, mfr, name, price, extra, new_id=pid)


if __name__ == "__main__":
    for step in (build_gpus, build_pro_gpus, build_water_gpus, build_cpus, build_motherboards, build_ram,
                 build_storage, build_psus, build_coolers, build_cases, build_fans, build_peripherals):
        step()
    write_all()
    with open(os.path.join(os.path.dirname(OUT), "manifest.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["table", "file", "id", "price", "template", "asset"])
        for b in built:
            w.writerow([b["table"], b["file"], b["rows"][0]["ID"], b["price"], b["tmpl"], b["asset"]])
    with open(os.path.join(os.path.dirname(OUT), "skipped.csv"), "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows([("table", "manufacturer", "name", "reason"), *skipped])
    counts = {}
    for b in built:
        counts[b["table"]] = counts.get(b["table"], 0) + 1
    print("built", len(built), counts)
    print("skipped", len(skipped), {r: sum(1 for s in skipped if s[3] == r) for r in {s[3] for s in skipped}})
