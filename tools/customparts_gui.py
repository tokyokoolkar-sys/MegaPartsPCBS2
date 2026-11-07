"""CustomParts GUI: drop a .glb (or .blend, exported through Blender) model in, fill in the card, press Build.

It does everything that used to be manual for a new custom GPU:
  1. converts the .glb into the Unity project (tools/glb_to_unity.py -> unity/ModelBundles/Assets/Models/<Name>/)
  2. guesses the model's reference parts (shroud, bracket, power connector, PCIe edge, fans) from node names and
     sizes, shown in drop-downs so you can correct them
  3. writes the part XML (stats copied from a template card, with your name / slots / length / VRAM / price)
     and the parts.txt line (added or replaced by part ID)
  4. runs tools/build_customparts.ps1, and Deploy copies out/customparts into the game (refused while it runs)

Run:  uv run --no-project --with tkinterdnd2 tools/customparts_gui.py
(tkinterdnd2 gives drag and drop; without it the window still works with the Browse button.)
"""
import html, json, math, os, re, shutil, subprocess, sys, threading
from dataclasses import dataclass
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore[import-not-found]
except ImportError:  # still usable, just without drag and drop
    TkinterDnD, DND_FILES = None, "DND_Files"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = r"E:\Games\PC.Building.Simulator.2.v1.17.02"
MODELS = os.path.join(ROOT, "unity", "ModelBundles", "Assets", "Models")
PARTS_DIR = os.path.join(ROOT, "mod", "CustomParts")
PARTS_TXT = os.path.join(PARTS_DIR, "parts.txt")
XML_DIR = os.path.join(PARTS_DIR, "parts")
STAGE = os.path.join(ROOT, "out", "customparts")

# Base cards whose prefab the custom part reuses, with the stock reference meshes the mod lines the model up on.
@dataclass(frozen=True)
class Base:
    key: str
    stock_mm: int
    shroud: str
    bracket: str
    top: str
    board: str
    hide: str
    fans: tuple
    port: str
    scale: str = ""  # "@<units per metre>": fixed game scale, for bases whose body length isn't a known real size


BASES = {
    "RTX 4090 FE (2-3 slot air cooler)": Base(
        key="Prefabs/GPU/NVidia/GPU_NVIDIA_GEFORCE_RTX_4090", stock_mm=304,
        shroud="4090_Body", bracket="4090_Chassis_Bracket", top="16 pin power connector", board="4090_PCB",
        hide="4090_, Circle, Cylinder, Plane, Test_", fans=("4090_Fan_01", "4090_Fan_02"),
        port="16 pin power connector"),
    # One merged body mesh (no separate bracket / PCB): lines up on the whole card (bracket tab bottom, back face,
    # HDMI port at the bracket end). Three game fans, so the fan control app lists three.
    "MSI RTX 5070/5080 INSPIRE 3X (3 fans, merged body)": Base(
        key="Prefabs/GPU/MSI/GPU_MSI_GeForce_RTX_5070_12G_INSPIRE_3X", stock_mm=0,
        shroud="MSI_GeForce_RTX_5070_12G_INSPIRE_3X", bracket="HDMI", top="16 pin power connector", board="*",
        hide="MSI_, Fan", fans=("Fan1", "Fan2", "Fan3"), port="16 pin power connector", scale="@5.084"),
}

# Name hints for guessing the model's reference nodes (lower-case substrings, best first).
HINTS = {
    "shroud": ["main frame", "shroud", "frame", "body", "cover", "case", "heatsink"],
    "bracket": ["io plate", "io_plate", "bracket", "io", "plate"],
    "top": ["power port", "power", "pin", "connector", "12v"],
    "board": ["pcie", "pci", "finger", "pcb", "board"],
    "fans": ["blade", "fan"],
}


# ---------- model.json helpers ----------

def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def qrot(q, v):
    x, y, z, w = q
    tx, ty, tz = 2 * (y * v[2] - z * v[1]), 2 * (z * v[0] - x * v[2]), 2 * (x * v[1] - y * v[0])
    return (v[0] + w * tx + (y * tz - z * ty), v[1] + w * ty + (z * tx - x * tz), v[2] + w * tz + (x * ty - y * tx))


def node_bounds(model):
    """World-space (model root) bounds of every node with a mesh, composing the parent chain."""
    nodes = model["nodes"]
    world = {}

    def get(i):
        if i in world:
            return world[i]
        n = nodes[i]
        if n["parent"] < 0:
            w = (tuple(n["t"]), tuple(n["r"]), tuple(n["s"]))
        else:
            pt, pr, ps = get(n["parent"])
            local = tuple(n["t"][k] * ps[k] for k in range(3))
            t = tuple(pt[k] + qrot(pr, local)[k] for k in range(3))
            w = (t, qmul(pr, tuple(n["r"])), tuple(ps[k] * n["s"][k] for k in range(3)))
        world[i] = w
        return w

    out = {}
    for i, n in enumerate(nodes):
        if n["mesh"] < 0:
            continue
        t, r, s = get(i)
        p = model["meshes"][n["mesh"]]["pos"]
        lo, hi = [math.inf] * 3, [-math.inf] * 3
        for j in range(0, len(p), 3):
            v = qrot(r, (p[j] * s[0], p[j + 1] * s[1], p[j + 2] * s[2]))
            for k in range(3):
                c = v[k] + t[k]
                lo[k] = min(lo[k], c); hi[k] = max(hi[k], c)
        out[n["name"]] = (lo, hi)
    return out


def guess(bounds):
    """Best guess per reference role, from node names, falling back to sizes for the shroud."""
    names = list(bounds)
    vol = {n: math.prod(max(h - l, 1e-9) for l, h in zip(*bounds[n])) for n in names}

    def by_hint(role, exclude=()):
        for h in HINTS[role]:
            for n in sorted(names, key=lambda n: -vol[n]):
                if h in n.lower() and n not in exclude:
                    return n
        return ""

    g = {"shroud": by_hint("shroud") or max(names, key=lambda n: vol[n], default="")}
    g["bracket"] = by_hint("bracket", (g["shroud"],))
    g["top"] = by_hint("top", (g["shroud"],))
    g["board"] = by_hint("board", (g["shroud"],))
    fans = [n for n in names if any(h in n.lower() for h in HINTS["fans"]) and "holder" not in n.lower()
            and "hub" not in n.lower() and "cover" not in n.lower()]
    g["fans"] = sorted(fans)[:3]
    shape = guess_by_shape(bounds)
    for k in ("bracket", "top", "board"):
        g[k] = g[k] or shape[k]
    g["fans"] = g["fans"] or shape["fans"]
    return g


def guess_by_shape(bounds):
    """Reference parts from geometry, for models with generic node names (Cube.003, Plane.010...).
    Card axes: length = longest side of the whole model, thickness = shortest; height = the other one.
    Bracket: thin along the length, nearly full height, at one end. Board: thin flat plate, long and tall
    (the PCB). Up: the side the bracket doesn't stick out past the board (bracket tab hangs below).
    Power connector: biggest small block near the top edge. Fans: round flat discs, largest first."""
    out = {"bracket": "", "top": "", "board": "", "fans": []}
    if not bounds:
        return out
    lo = [min(b[0][k] for b in bounds.values()) for k in range(3)]
    hi = [max(b[1][k] for b in bounds.values()) for k in range(3)]
    size = [h - l for l, h in zip(lo, hi)]
    L = max(range(3), key=lambda k: size[k]); T = min(range(3), key=lambda k: size[k]); H = 3 - L - T
    sz = {n: [b[1][k] - b[0][k] for k in range(3)] for n, b in bounds.items()}

    br = [n for n in bounds if sz[n][L] < 0.08 * size[L] and sz[n][H] > 0.6 * size[H]
          and min(bounds[n][0][L] - lo[L], hi[L] - bounds[n][1][L]) < 0.05 * size[L]]
    out["bracket"] = max(br, key=lambda n: sz[n][H], default="")

    bd = [n for n in bounds if sz[n][T] < 0.03 * size[L] and sz[n][L] > 0.3 * size[L] and sz[n][H] > 0.3 * size[H]]
    out["board"] = max(bd, key=lambda n: sz[n][L] * sz[n][H], default="")

    up = 1
    if out["bracket"] and out["board"]:
        b, p = bounds[out["bracket"]], bounds[out["board"]]
        up = 1 if (p[0][H] - b[0][H]) >= (b[1][H] - p[1][H]) else -1
    top_edge = hi[H] if up > 0 else lo[H]
    tp = [n for n in bounds if max(sz[n]) < 0.12 * size[L] and min(sz[n]) > 0.02 * size[L]
          and abs((bounds[n][1][H] if up > 0 else bounds[n][0][H]) - top_edge) < 0.15 * size[H]]
    out["top"] = max(tp, key=lambda n: math.prod(sz[n]), default="")

    taken = {out["bracket"], out["board"], out["top"]}
    def round_disc(n):
        a, b2 = sorted((sz[n][L], sz[n][H]))
        return n not in taken and a > 0.2 * size[L] and a / b2 > 0.95 and sz[n][T] < 0.4 * a
    discs = sorted((n for n in bounds if round_disc(n)), key=lambda n: (-round(sz[n][L], 2), n))
    if discs:
        d0 = round(sz[discs[0]][L], 2)
        out["fans"] = sorted((n for n in discs if round(sz[n][L], 2) == d0), key=lambda n: bounds[n][0][L])[:3]
    return out


# ---------- part tables ----------

def parse_xml(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    return {html.unescape(k): html.unescape(v) for k, v in re.findall(r'<td div="([^"]*)">(.*?)</td>', txt, re.S)}


def templates():
    """Stats templates: our own custom part XMLs first, then the stock GPU table."""
    out = {}
    for f in sorted(os.listdir(XML_DIR)) if os.path.isdir(XML_DIR) else []:
        if f.endswith(".xml"):
            row = parse_xml(os.path.join(XML_DIR, f))
            out[f"[custom] {row.get('Manufacturer', '')} {row.get('Part Name', f)}"] = row
    d = json.load(open(os.path.join(ROOT, "data", "GPU.json"), encoding="utf-8"))
    for r in d["rows"]:
        if r.get("ID") and r.get("Part Name"):
            out.setdefault(f"{r.get('Manufacturer', '')} {r['Part Name']} ({r['ID']})", r)
    return out, d["header"]


def write_xml(path, title, header, row):
    cells = "".join(f'\t\t<td div="{html.escape(c)}">{html.escape(str(row.get(c, "")), quote=False)}</td>\n' for c in header)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(f"{title}\n<table>\n\t<tr>\n{cells}\t</tr>\n</table>\n")


def upsert_parts_line(part_id, line):
    lines = open(PARTS_TXT, encoding="utf-8").read().splitlines() if os.path.exists(PARTS_TXT) else []
    for i, l in enumerate(lines):
        if not l.lstrip().startswith("#") and l.split("|")[0].strip() == part_id:
            # Keep tuned offset / rotation (fields 14-15) when rebuilding an existing part.
            old = [x.strip() for x in l.split("|")]
            new = [x.strip() for x in line.split("|")]
            new += old[len(new):]
            lines[i] = " | ".join(new)
            break
    else:
        lines.append(line)
    open(PARTS_TXT, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def find_blender():
    """blender.exe from the BLENDER variable, PATH, or the usual install folders (newest version first)."""
    if os.environ.get("BLENDER") and os.path.exists(os.environ["BLENDER"]):
        return os.environ["BLENDER"]
    found = shutil.which("blender")
    if found:
        return found
    roots = [os.path.join(os.environ.get(v, ""), "Blender Foundation") for v in ("ProgramFiles", "ProgramFiles(x86)")]
    roots.append(r"C:\Program Files (x86)\Steam\steamapps\common\Blender")
    cands = []
    for r in roots:
        if os.path.exists(os.path.join(r, "blender.exe")):
            cands.append(os.path.join(r, "blender.exe"))
        if os.path.isdir(r):
            cands += [os.path.join(r, d, "blender.exe") for d in os.listdir(r) if os.path.exists(os.path.join(r, d, "blender.exe"))]
    return sorted(cands)[-1] if cands else None


def game_running():
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq PCBS2.exe"], capture_output=True, text=True).stdout
        return "PCBS2.exe" in out
    except OSError:
        return False


# ---------- window ----------

class App:
    def __init__(self, root):
        self.root = root
        root.title("PCBS2 CustomParts")
        root.geometry("760x720")
        self.model_names = []
        self.templates, self.header = templates()
        self.v = {k: tk.StringVar() for k in
                  "glb name part_name manufacturer slots length vram price template base shroud bracket top board fan1 fan2 fan3".split()}
        self.v["base"].set(next(iter(BASES)))
        self.v["slots"].set("2"); self.v["length"].set("304")
        self.rebuild_unity = tk.BooleanVar(value=True)

        f = ttk.Frame(root, padding=10); f.pack(fill="both", expand=True)
        drop = tk.Label(f, text="Drop a .glb or .blend model here\n(or Browse)", relief="groove", height=4, bg="#f4f4f4")
        drop.pack(fill="x")
        if TkinterDnD:
            getattr(drop, "drop_target_register")(DND_FILES)
            getattr(drop, "dnd_bind")("<<Drop>>", lambda e: self.load_model(root.tk.splitlist(e.data)[0]))
        else:
            drop.config(text="Drag and drop needs tkinterdnd2 (see the file header); use Browse")
        row = ttk.Frame(f); row.pack(fill="x", pady=4)
        ttk.Button(row, text="Browse...", command=self.browse).pack(side="left")
        ttk.Label(row, textvariable=self.v["glb"]).pack(side="left", padx=8)

        card = ttk.LabelFrame(f, text="Card", padding=6); card.pack(fill="x", pady=4)
        self.field(card, "Model name (folder / bundle)", "name", 0)
        self.field(card, "Part name (shown in game)", "part_name", 1)
        self.field(card, "Manufacturer", "manufacturer", 2)
        self.field(card, "Slot size", "slots", 3, w=6)
        self.field(card, "Shroud length mm", "length", 4, w=6)
        self.field(card, "VRAM GB (blank = template)", "vram", 5, w=6)
        self.field(card, "Price (blank = template)", "price", 6, w=8)
        ttk.Label(card, text="Stats template").grid(row=7, column=0, sticky="w")
        ttk.Combobox(card, textvariable=self.v["template"], values=list(self.templates), width=60).grid(row=7, column=1, sticky="w")
        ttk.Label(card, text="Base card (game behaviour)").grid(row=8, column=0, sticky="w")
        ttk.Combobox(card, textvariable=self.v["base"], values=list(BASES), state="readonly", width=40).grid(row=8, column=1, sticky="w")

        refs = ttk.LabelFrame(f, text="Model reference parts (guessed from names; check them)", padding=6)
        refs.pack(fill="x", pady=4)
        self.combos = []
        for i, (label, key) in enumerate([("Shroud (longest side = length)", "shroud"), ("Bracket / IO plate", "bracket"),
                                          ("Power connector (top edge)", "top"), ("PCIe edge / board", "board"),
                                          ("Fan 1 (spins with stock fan 1)", "fan1"), ("Fan 2", "fan2"),
                                          ("Fan 3 (spins with stock fan 1)", "fan3")]):
            ttk.Label(refs, text=label).grid(row=i, column=0, sticky="w")
            c = ttk.Combobox(refs, textvariable=self.v[key], width=40); c.grid(row=i, column=1, sticky="w")
            self.combos.append(c)

        btns = ttk.Frame(f); btns.pack(fill="x", pady=6)
        ttk.Checkbutton(btns, text="Rebuild models in Unity (slow; needed for a new model)", variable=self.rebuild_unity).pack(side="left")
        ttk.Button(btns, text="Deploy to game", command=self.deploy).pack(side="right")
        ttk.Button(btns, text="Build", command=self.build).pack(side="right", padx=6)
        self.log = tk.Text(f, height=14, font=("Consolas", 9)); self.log.pack(fill="both", expand=True)
        self.say(f"Project: {ROOT}")

    def field(self, parent, label, key, r, w=40):
        ttk.Label(parent, text=label).grid(row=r, column=0, sticky="w")
        ttk.Entry(parent, textvariable=self.v[key], width=w).grid(row=r, column=1, sticky="w")

    def say(self, msg):
        self.root.after(0, lambda: (self.log.insert("end", msg + "\n"), self.log.see("end")))

    def blend_to_glb(self, path):
        """Export a .blend to out/blend/<name>.glb with Blender in the background (node names are kept)."""
        exe = find_blender()
        if not exe:
            messagebox.showerror("CustomParts", "Blender not found. Install it (blender.org, or winget install "
                                 "BlenderFoundation.Blender), or set BLENDER to blender.exe's path.")
            return None
        out = os.path.join(ROOT, "out", "blend")
        os.makedirs(out, exist_ok=True)
        glb = os.path.join(out, os.path.splitext(os.path.basename(path))[0] + ".glb")
        expr = ("import bpy, sys; bpy.ops.export_scene.gltf(filepath=sys.argv[-1], export_format='GLB', "
                "export_apply=True, export_yup=True, use_visible=False)")
        self.say(f"Exporting {path} with {exe}")
        r = subprocess.run([exe, "-b", path, "--factory-startup", "--python-expr", expr, "--", glb],
                           capture_output=True, text=True)
        tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-8:])
        self.say(tail)
        if r.returncode != 0 or not os.path.exists(glb):
            messagebox.showerror("CustomParts", "Blender export failed; see the log.")
            return None
        self.say(f"Exported {glb}")
        return glb

    def browse(self):
        p = filedialog.askopenfilename(filetypes=[("3D model", "*.glb *.blend"), ("glTF binary", "*.glb"), ("Blender", "*.blend")])
        if p:
            self.load_model(p)

    def load_model(self, path):
        src = path
        if path.lower().endswith(".blend"):
            path = self.blend_to_glb(path)
            if not path:
                return
        elif not path.lower().endswith(".glb"):
            messagebox.showerror("CustomParts", "Drop a .glb or .blend model.")
            return
        self.v["glb"].set(path)
        path_name = os.path.splitext(os.path.basename(src))[0]
        base = re.sub(r"[^A-Za-z0-9]", "", path_name) or "Model"
        if not self.v["name"].get():
            self.v["name"].set(base)
        if not self.v["part_name"].get():
            self.v["part_name"].set(path_name + " (Custom Model)")
        name = self.v["name"].get()
        dst = os.path.join(MODELS, name)
        self.say(f"Converting {path} -> {dst}")
        r = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "tools", "glb_to_unity.py"), path, dst],
                           capture_output=True, text=True)
        self.say((r.stdout + r.stderr).strip())
        if r.returncode != 0:
            messagebox.showerror("CustomParts", "Conversion failed; see the log.")
            return
        model = json.load(open(os.path.join(dst, "model.json")))
        bounds = node_bounds(model)
        self.model_names = sorted(bounds)
        for c in self.combos:
            c["values"] = self.model_names
        g = guess(bounds)
        for k in ("shroud", "bracket", "top", "board"):
            self.v[k].set(g[k])
        fans = list(g["fans"]) + ["", "", ""]
        self.v["fan1"].set(fans[0]); self.v["fan2"].set(fans[1]); self.v["fan3"].set(fans[2])
        self.say(f"{len(self.model_names)} mesh nodes. Guessed: shroud '{g['shroud']}', bracket '{g['bracket']}', "
                 f"top '{g['top']}', board '{g['board']}', fans {g['fans']}")

    def build(self):
        name = self.v["name"].get().strip()
        if not name or not os.path.exists(os.path.join(MODELS, name, "model.json")):
            messagebox.showerror("CustomParts", "Drop a model first.")
            return
        missing = [k for k in ("shroud", "bracket", "top", "board") if not self.v[k].get()]
        if missing:
            messagebox.showerror("CustomParts", "Pick model parts for: " + ", ".join(missing))
            return
        tpl = self.templates.get(self.v["template"].get())
        if tpl is None:
            messagebox.showerror("CustomParts", "Pick a stats template card.")
            return
        b = BASES[self.v["base"].get()]
        part_id = f"GPU_CustomParts_{name}"
        key = f"Prefabs/Custom/GPU_{name}"

        row = dict(tpl)
        row.update({"ID": part_id, "Part Name": self.v["part_name"].get(), "Class": "Modded",
                    "Slot Size": self.v["slots"].get(), "Length": self.v["length"].get(), "Asset Path": key,
                    "Notes": "PCBS2 CustomParts", "In Shop": "Yes", "Start In Freebuild Inventory": "Yes"})
        for k, col in (("manufacturer", "Manufacturer"), ("vram", "VRAM (GB)"), ("price", "Price")):
            if self.v[k].get().strip():
                row[col] = self.v[k].get().strip()
        row["Concat name"] = f"({row.get('Level', '')}) {row.get('Manufacturer', '')} {row['Part Name']}"
        os.makedirs(XML_DIR, exist_ok=True)
        title = f"AirCooledGPU_{row.get('Manufacturer', '')} {row['Part Name']}"
        xml = os.path.join(XML_DIR, re.sub(r'[<>:"/\\|?*]', "", title) + ".xml")
        header = self.header if all(c in self.header for c in row if c) else list(row)
        write_xml(xml, title, header, row)
        self.say(f"Wrote {xml}")

        fans = [f for f in (self.v["fan1"].get(), self.v["fan2"].get(), self.v["fan3"].get()) if f]
        # A third model fan spins with stock fan 1 (the 4090 has two).
        fan_field = ", ".join(f"{m}={b.fans[i % len(b.fans)]}" for i, m in enumerate(fans))
        line = " | ".join([part_id, key, b.key, name.lower(), name, f"{b.scale or b.stock_mm}/{self.v['length'].get()}",
                           f"{b.shroud}={self.v['shroud'].get()}", f"{b.bracket}={self.v['bracket'].get()}",
                           f"{b.top}={self.v['top'].get()}", f"{b.board}={'*' if b.board == '*' else self.v['board'].get()}", b.hide,
                           fan_field, f"{self.v['top'].get()}={b.port}"])
        upsert_parts_line(part_id, line)
        self.say(f"parts.txt: {part_id}")

        args = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                os.path.join(ROOT, "tools", "build_customparts.ps1")]
        if not self.rebuild_unity.get():
            args.append("-SkipUnity")
        self.say("Building (Unity can take a few minutes)...")

        def run():
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for l in p.stdout or ():
                self.say(l.rstrip())
            self.say("BUILD OK - press Deploy" if p.wait() == 0 else f"BUILD FAILED (exit {p.returncode})")
        threading.Thread(target=run, daemon=True).start()

    def deploy(self):
        if game_running():
            messagebox.showwarning("CustomParts", "Close the game first (it locks CustomParts.dll).")
            return
        src = os.path.join(STAGE, "Mods")
        if not os.path.isdir(src):
            messagebox.showerror("CustomParts", "Nothing staged yet; press Build first.")
            return
        game_cfg = os.path.join(GAME, "Mods", "CustomParts", "parts.txt")
        if os.path.exists(game_cfg):
            # The in-game tuner saves offsets into the game's copy; carry them back before overwriting.
            tuned = {l.split("|")[0].strip(): [x.strip() for x in l.split("|")]
                     for l in open(game_cfg, encoding="utf-8") if l.strip() and not l.lstrip().startswith("#")}
            for pid, f in tuned.items():
                if len(f) > 13:
                    lines = open(PARTS_TXT, encoding="utf-8").read().splitlines()
                    for i, l in enumerate(lines):
                        cur = [x.strip() for x in l.split("|")]
                        if not l.lstrip().startswith("#") and cur[0] == pid:
                            lines[i] = " | ".join(cur[:13] + f[13:])
                    open(PARTS_TXT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
            shutil.copy2(PARTS_TXT, os.path.join(STAGE, "Mods", "CustomParts", "parts.txt"))
        n = 0
        for d, _, files in os.walk(src):
            for fn in files:
                rel = os.path.relpath(os.path.join(d, fn), src)
                dst = os.path.join(GAME, "Mods", rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(os.path.join(d, fn), dst)
                n += 1
        self.say(f"Deployed {n} file(s) to {GAME}\\Mods (tuned offsets kept)")


if __name__ == "__main__":
    tk_root = TkinterDnD.Tk() if TkinterDnD else tk.Tk()
    App(tk_root)
    tk_root.mainloop()
