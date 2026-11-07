"""Generate sTR5 (DDR5) Threadripper parts: Threadripper PRO 7995WX / 9995WX and three TRX50 boards.

The socket "sTR5" is added by PCBS2.SocketLoader (addons\\PCBS2.SocketLoader\\sockets.ini: 100 = sTR5).
Models are the game's own: CPUs reuse the Threadripper 3990X prefab, boards reuse TRX40 board prefabs
of the same form factor. Stats start from the stock 3990X / TRX40 rows and are changed where the real
part differs (cores, clocks, wattage, DDR5, prices). CPU Series is the same-generation desktop Ryzen\nseries (Zen 4 / Zen 5): the game caps XMP RAM speed per series, and thread3000 kept DDR5 near 5000. Benchmark scores are estimates scaled from the
stock table (Ryzen 9 9950X3D ~16k Time Spy CPU), not measured values.

Writes the XMLs to out/threadripper/. Run: python tools/gen_threadripper.py
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "threadripper")
SOCKET = "sTR5"


def table(name):
    d = json.load(open(os.path.join(ROOT, "data", name), encoding="utf-8"))
    return d["header"], {r["ID"]: r for r in d["rows"] if r.get("ID")}


def write(fname, title, header, row):
    cells = "".join(f'\t\t<td div="{html.escape(c)}">{html.escape(str(row.get(c, "")), quote=False)}</td>\n' for c in header)
    with open(os.path.join(OUT, fname), "w", encoding="utf-8", newline="") as f:
        f.write(f"{title}\n<table>\n\t<tr>\n{cells}\t</tr>\n</table>\n")


def concat(row):
    return f"({row['Level']}) {row['Manufacturer']} {row['Part Name']}"


CPUS = [
    dict(ID="CPU_MegaParts_TRPRO_7995WX", **{"Part Name": "Ryzen Threadripper PRO 7995WX", "Price": "9999",
         "Level": "20", "Percent Through": "1", "Frequency": "5100", "Base Frequency": "2500",
         "Basic CPU Score (TS)": "24000", "Basic CPU Score (TSX)": "20000", "Max Freq": "5200",
         "Overclock Basic CPU Score": "24300", "Default Memory Speed": "5200", "CPU Series": "ryzen7000",
         "Timeframe": "Wed Nov 01 2023 00:00:00 GMT+0000 (Greenwich Mean Time)",
         "Product Page": "https://www.amd.com/en/products/processors/workstations/ryzen-threadripper.html"}),
    dict(ID="CPU_MegaParts_TRPRO_9995WX", **{"Part Name": "Ryzen Threadripper PRO 9995WX", "Price": "11699",
         "Level": "20", "Percent Through": "50", "Frequency": "5400", "Base Frequency": "2500",
         "Basic CPU Score (TS)": "27000", "Basic CPU Score (TSX)": "23000", "Max Freq": "5500",
         "Overclock Basic CPU Score": "27300", "Default Memory Speed": "6400", "CPU Series": "ryzen9000",
         "Timeframe": "Tue Jul 01 2025 00:00:00 GMT+0100 (British Summer Time)",
         "Product Page": "https://www.amd.com/en/products/processors/workstations/ryzen-threadripper.html"}),
]

# (new ID, manufacturer, name, base board ID (same form factor), price, product page)
BOARDS = [
    ("Motherboard_MegaParts_TRX50_SAGE", "ASUS", "Pro WS TRX50-SAGE WIFI", "Motherboard_ASUS_22", "900",
     "https://www.asus.com/motherboards-components/motherboards/workstation/pro-ws-trx50-sage-wifi/"),
    ("Motherboard_MegaParts_TRX50_WS", "ASRock", "TRX50 WS", "Motherboard_ASROCK_22", "800",
     "https://www.asrock.com/mb/AMD/TRX50%20WS/"),
    ("Motherboard_MegaParts_TRX50_AEROD", "GIGABYTE", "TRX50 AERO D", "Motherboard_GIGABYTE_30", "850",
     "https://www.gigabyte.com/Motherboard/TRX50-AERO-D-rev-10"),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    ch, cpus = table("CPU.json")
    for c in CPUS:
        row = dict(cpus["CPU_AMD_15"])  # Threadripper 3990X: model, TR score coefficients
        row.update(c)
        row.update({"Cores": "96", "Threads": "192", "Efficiency Cores": "0", "Wattage": "350", "Voltage": "1.2",
                    "Max Voltage": "1.35", "DDR4": "No", "DDR5": "Yes", "Supported Memory Types": "DDR5,",
                    "Mem Type Performance Target": "DDR5", "Number of dies": "12", "Max Memory Channels": "4",
                    "CPU Socket": SOCKET, "SellPrice": str(int(c["Price"]) // 3), "In Open Beta": "No",
                    "PCBS": "2", "Class": "Modded", "% increase": "1.25", "Overclock CPU score increase": "1.25",
                    "Chipset (Lookup)": c["Part Name"], "Chipset (UI)": c["Part Name"], "Integrated Graphics": "false",
                    "Score to value ratio": "2.5", "Target Score to Value ratio": "2.5",
                    "Notes": "PCBS2 MegaParts sTR5 (needs PCBS2.SocketLoader socket 100 = sTR5)"})
        row["Concat name"] = concat(row)
        write(f"CPU_AMD {c['Part Name']}.xml", f"CPU_AMD {c['Part Name']}", ch, row)

    mh, boards = table("Motherboard.json")
    for bid, man, name, base, price, page in BOARDS:
        row = dict(boards[base])
        row.update({"ID": bid, "Manufacturer": man, "Part Name": name, "Price": price,
                    "SellPrice": str(int(price) // 3), "Level": "20", "Percent Through": "1", "PCBS": "2",
                    "Class": "Modded", "In Open Beta": "No", "Chipset": "TRX50", "CPU Socket": SOCKET,
                    "Ram Type": "DDR5", "Default Memory Speed": "5200",
                    "Memory Speed Steps": "4400,4800,5200,5600,6000,6400,6800,7200,7600,8000",
                    "Max Memory Speed": "8000", "Product Page": page, "Licensor Approved": "Yes",
                    "Notes": "PCBS2 MegaParts sTR5; model reused from " + boards[base]["Part Name"]})
        row["Concat name"] = concat(row)
        write(f"Motherboard_{man} {name}.xml", f"Motherboard_{man} {name}", mh, row)
    print("\n".join(sorted(os.listdir(OUT))))


if __name__ == "__main__":
    main()
