"""Real-world part catalog for PCBS2 MegaParts.

Every entry is turned into one XML part by build.py, which clones a stock game
row of the same kind (so benchmark keys, prefab paths and unknown columns stay
valid) and overrides the fields given here. Prices are in-game dollars.
"""

# ---------------------------------------------------------------- GPUs
# Stock chipset key -> display name used in part names.
NV40 = ["GeForce RTX 4060", "GeForce RTX 4060 Ti", "GeForce RTX 4070", "Geforce RTX 4070 SUPER",
        "GeForce RTX 4070 Ti SUPER", "GeForce RTX 4080", "Geforce RTX 4080 SUPER", "GeForce RTX 4090"]
NV50 = ["GeForce RTX 5050", "GeForce RTX 5060", "GeForce RTX 5060 Ti", "GeForce RTX 5070",
        "GeForce RTX 5070 Ti", "GeForce RTX 5080", "GeForce RTX 5090"]
RX7 = ["Radeon RX 7700 XT", "Radeon RX 7800 XT", "Radeon RX 7900 XT", "Radeon RX 7900 XTX"]
RX9 = ["Radeon RX 9060 XT", "Radeon RX 9070", "Radeon RX 9070 XT"]
ARC = ["Intel Arc A750", "Intel Arc A770", "Intel Arc B570", "Intel Arc B580"]

DISPLAY = {"Geforce RTX 4070 SUPER": "GeForce RTX 4070 SUPER", "Geforce RTX 4080 SUPER": "GeForce RTX 4080 SUPER",
           "Intel Arc A750": "Arc A750", "Intel Arc A770": "Arc A770", "Intel Arc B570": "Arc B570",
           "Intel Arc B580": "Arc B580"}

# Chipsets the game has no benchmark data for: (stock chipset to borrow, performance factor).
CHIPSET_FALLBACK = {"GeForce RTX 5060 Ti": ("GeForce RTX 5060", 1.2)}

# Chipsets sold with two memory sizes: every line gets both.
VRAM_VARIANTS = {"GeForce RTX 4060 Ti": [8, 16], "GeForce RTX 5060 Ti": [8, 16], "Radeon RX 9060 XT": [8, 16],
                 "Intel Arc A770": [16]}


def span(seq, lo, hi):
    """Chipsets in seq from lo to hi inclusive."""
    return seq[seq.index(lo):seq.index(hi) + 1]


# Tier: 0 = budget/base, 1 = mid, 2 = flagship. Drives clock, price and score bumps.
# (manufacturer, line name with {c} for the chipset, tier, chipsets)
GPU_LINES = [
    # ---- NVIDIA partners
    ("ASUS", "Dual {c} OC", 0, span(NV40, "GeForce RTX 4060", "Geforce RTX 4070 SUPER") + span(NV50, "GeForce RTX 5050", "GeForce RTX 5070")),
    ("ASUS", "Prime {c} OC", 0, span(NV50, "GeForce RTX 5060", "GeForce RTX 5080")),
    ("ASUS", "TUF Gaming {c} OC", 1, span(NV40, "GeForce RTX 4070", "GeForce RTX 4090") + span(NV50, "GeForce RTX 5070", "GeForce RTX 5090")),
    ("ASUS", "ROG Strix {c} OC", 2, span(NV40, "GeForce RTX 4060", "GeForce RTX 4090") + span(NV50, "GeForce RTX 5070", "GeForce RTX 5070 Ti")),
    ("ASUS", "ROG Astral {c} OC", 2, ["GeForce RTX 5080", "GeForce RTX 5090"]),
    ("MSI", "{c} Ventus 2X OC", 0, span(NV40, "GeForce RTX 4060", "Geforce RTX 4070 SUPER") + span(NV50, "GeForce RTX 5050", "GeForce RTX 5070")),
    ("MSI", "{c} Ventus 3X OC", 0, span(NV40, "GeForce RTX 4070", "GeForce RTX 4090") + span(NV50, "GeForce RTX 5070", "GeForce RTX 5090")),
    ("MSI", "{c} Gaming X Slim", 1, span(NV40, "GeForce RTX 4060", "GeForce RTX 4090")),
    ("MSI", "{c} Gaming Trio OC", 1, span(NV50, "GeForce RTX 5060", "GeForce RTX 5090")),
    ("MSI", "{c} Suprim X", 2, span(NV40, "GeForce RTX 4070 Ti SUPER", "GeForce RTX 4090") + span(NV50, "GeForce RTX 5070 Ti", "GeForce RTX 5090")),
    ("GIGABYTE", "{c} Windforce OC", 0, span(NV40, "GeForce RTX 4060", "GeForce RTX 4090") + span(NV50, "GeForce RTX 5060", "GeForce RTX 5090")),
    ("GIGABYTE", "{c} Eagle OC", 0, span(NV40, "GeForce RTX 4060", "Geforce RTX 4080 SUPER") + span(NV50, "GeForce RTX 5060", "GeForce RTX 5080")),
    ("GIGABYTE", "{c} Gaming OC", 1, span(NV40, "GeForce RTX 4060", "GeForce RTX 4090") + span(NV50, "GeForce RTX 5060", "GeForce RTX 5090")),
    ("GIGABYTE", "{c} Aero OC", 1, span(NV40, "GeForce RTX 4060 Ti", "Geforce RTX 4080 SUPER") + span(NV50, "GeForce RTX 5060", "GeForce RTX 5080")),
    ("GIGABYTE", "AORUS {c} Master", 2, span(NV40, "Geforce RTX 4070 SUPER", "GeForce RTX 4090") + span(NV50, "GeForce RTX 5070", "GeForce RTX 5090")),
    ("ZOTAC", "Gaming {c} Twin Edge OC", 0, span(NV40, "GeForce RTX 4060", "GeForce RTX 4070 Ti SUPER") + span(NV50, "GeForce RTX 5050", "GeForce RTX 5070")),
    ("ZOTAC", "Gaming {c} Trinity OC", 1, span(NV40, "GeForce RTX 4070 Ti SUPER", "GeForce RTX 4090")),
    ("ZOTAC", "Gaming {c} SOLID OC", 1, span(NV50, "GeForce RTX 5070", "GeForce RTX 5090")),
    ("ZOTAC", "Gaming {c} AMP Extreme AIRO", 2, span(NV40, "GeForce RTX 4070 Ti SUPER", "GeForce RTX 4090")),
    ("ZOTAC", "Gaming {c} AMP Extreme INFINITY", 2, ["GeForce RTX 5080", "GeForce RTX 5090"]),
    ("PNY", "{c} VERTO Dual Fan", 0, span(NV40, "GeForce RTX 4060", "Geforce RTX 4070 SUPER")),
    ("PNY", "{c} XLR8 Gaming VERTO EPIC-X RGB OC", 1, span(NV40, "Geforce RTX 4070 SUPER", "GeForce RTX 4090") + span(NV50, "GeForce RTX 5070", "GeForce RTX 5090")),
    ("Palit", "{c} Dual", 0, span(NV40, "GeForce RTX 4060", "Geforce RTX 4070 SUPER") + span(NV50, "GeForce RTX 5060", "GeForce RTX 5070")),
    ("Palit", "{c} GamingPro OC", 1, span(NV40, "GeForce RTX 4070", "GeForce RTX 4090") + span(NV50, "GeForce RTX 5070", "GeForce RTX 5090")),
    ("Palit", "{c} GameRock OC", 2, span(NV40, "GeForce RTX 4070 Ti SUPER", "GeForce RTX 4090") + span(NV50, "GeForce RTX 5070 Ti", "GeForce RTX 5090")),
    ("Gainward", "{c} Ghost", 0, span(NV40, "GeForce RTX 4060", "Geforce RTX 4070 SUPER") + span(NV50, "GeForce RTX 5060", "GeForce RTX 5070")),
    ("Gainward", "{c} Phoenix GS", 1, span(NV40, "GeForce RTX 4070", "GeForce RTX 4090") + span(NV50, "GeForce RTX 5070", "GeForce RTX 5090")),
    ("INNO3D", "{c} Twin X2 OC", 0, span(NV40, "GeForce RTX 4060", "Geforce RTX 4070 SUPER") + span(NV50, "GeForce RTX 5060", "GeForce RTX 5070")),
    ("INNO3D", "{c} X3 OC", 1, span(NV40, "GeForce RTX 4070", "GeForce RTX 4090") + span(NV50, "GeForce RTX 5070", "GeForce RTX 5090")),
    # ---- AMD partners
    ("Sapphire", "PULSE {c}", 0, RX7 + RX9),
    ("Sapphire", "PURE {c}", 1, ["Radeon RX 7700 XT", "Radeon RX 7800 XT", "Radeon RX 7900 XT", "Radeon RX 9070", "Radeon RX 9070 XT"]),
    ("Sapphire", "NITRO+ {c}", 2, RX7 + ["Radeon RX 9060 XT", "Radeon RX 9070", "Radeon RX 9070 XT"]),
    ("PowerColor", "Fighter {c}", 0, ["Radeon RX 7700 XT", "Radeon RX 7800 XT"]),
    ("PowerColor", "Hellhound {c}", 1, RX7 + RX9),
    ("PowerColor", "Reaper {c}", 0, RX9),
    ("PowerColor", "Red Devil {c}", 2, RX7 + ["Radeon RX 9070", "Radeon RX 9070 XT"]),
    ("XFX", "Speedster SWFT {c}", 0, RX7 + RX9),
    ("XFX", "Speedster MERC 310 {c}", 2, ["Radeon RX 7900 XT", "Radeon RX 7900 XTX"]),
    ("XFX", "Speedster QICK 319 {c}", 1, ["Radeon RX 7700 XT", "Radeon RX 7800 XT"]),
    ("XFX", "Quicksilver {c} OC", 1, ["Radeon RX 9070", "Radeon RX 9070 XT"]),
    ("XFX", "Mercury {c} OC", 2, ["Radeon RX 9070", "Radeon RX 9070 XT"]),
    ("ASUS", "TUF Gaming {c} OC", 1, RX7 + ["Radeon RX 9070", "Radeon RX 9070 XT"]),
    ("ASUS", "Prime {c} OC", 0, RX9),
    ("ASUS", "Dual {c} OC", 0, ["Radeon RX 7700 XT", "Radeon RX 7800 XT", "Radeon RX 9060 XT"]),
    ("GIGABYTE", "{c} Gaming OC", 1, RX7 + RX9),
    ("GIGABYTE", "AORUS {c} Elite", 2, ["Radeon RX 7900 XTX", "Radeon RX 9070 XT"]),
    ("MSI", "{c} Gaming Trio OC", 1, ["Radeon RX 7900 XTX", "Radeon RX 9070", "Radeon RX 9070 XT"]),
    ("MSI", "{c} Gaming OC", 0, ["Radeon RX 9060 XT"]),
    ("ASRock", "{c} Challenger OC", 0, RX7),
    ("ASRock", "{c} Steel Legend", 1, RX7),
    ("ASRock", "{c} Phantom Gaming OC", 2, ["Radeon RX 7800 XT", "Radeon RX 7900 XT", "Radeon RX 7900 XTX"]),
    ("ASRock", "{c} Taichi OC", 2, ["Radeon RX 7900 XTX", "Radeon RX 9070 XT"]),
    # ---- Intel Arc partners
    ("ASRock", "Intel {c} Challenger OC", 0, ARC),
    ("ASRock", "Intel {c} Steel Legend", 1, ["Intel Arc B570", "Intel Arc B580"]),
    ("Sparkle", "Intel {c} Titan OC", 1, ARC),
    ("Acer", "Predator BiFrost Intel {c} OC", 1, ["Intel Arc A750", "Intel Arc A770"]),
    ("Acer", "Nitro Intel {c} OC", 1, ["Intel Arc B570", "Intel Arc B580"]),
    ("GUNNIR", "Intel {c} Photon", 0, ["Intel Arc A750", "Intel Arc A770", "Intel Arc B580"]),
]

# ---------------------------------------------------------------- CPUs
# name, manufacturer, stock template part name, boost MHz, cores, e-cores, threads,
# watts, unlocked, price factor vs template
CPUS = [
    # Intel 12th gen (LGA 1700)
    ("Core i3-12100F", "Intel", "Core i5-12600K", 4300, 4, 0, 8, 58, False, 0.33),
    ("Core i5-12400F", "Intel", "Core i5-12600K", 4400, 6, 0, 12, 65, False, 0.55),
    ("Core i5-12400", "Intel", "Core i5-12600K", 4400, 6, 0, 12, 65, False, 0.65),
    ("Core i5-12600KF", "Intel", "Core i5-12600K", 4900, 10, 4, 16, 125, True, 0.91),
    ("Core i7-12700F", "Intel", "Core i7-12700K", 4900, 12, 4, 20, 65, False, 0.78),
    ("Core i7-12700", "Intel", "Core i7-12700K", 4900, 12, 4, 20, 65, False, 0.83),
    ("Core i7-12700KF", "Intel", "Core i7-12700K", 5000, 12, 4, 20, 125, True, 0.94),
    ("Core i9-12900F", "Intel", "Core i9-12900K", 5100, 16, 8, 24, 65, False, 0.79),
    ("Core i9-12900KF", "Intel", "Core i9-12900K", 5200, 16, 8, 24, 125, True, 0.96),
    ("Core i9-12900KS", "Intel", "Core i9-12900K", 5500, 16, 8, 24, 150, True, 1.25),
    # Intel 13th gen
    ("Core i3-13100F", "Intel", "Core i5-13600K", 4500, 4, 0, 8, 58, False, 0.34),
    ("Core i5-13400F", "Intel", "Core i5-13600K", 4600, 10, 6, 16, 65, False, 0.61),
    ("Core i5-13400", "Intel", "Core i5-13600K", 4600, 10, 6, 16, 65, False, 0.69),
    ("Core i5-13500", "Intel", "Core i5-13600K", 4800, 14, 8, 20, 65, False, 0.73),
    ("Core i5-13600", "Intel", "Core i5-13600K", 5000, 14, 8, 20, 65, False, 0.81),
    ("Core i7-13700F", "Intel", "Core i7-13700K", 5200, 16, 8, 24, 65, False, 0.88),
    ("Core i7-13700", "Intel", "Core i7-13700K", 5200, 16, 8, 24, 65, False, 0.94),
    ("Core i9-13900F", "Intel", "Core i9-13900K", 5600, 24, 16, 32, 65, False, 0.89),
    ("Core i9-13900", "Intel", "Core i9-13900K", 5600, 24, 16, 32, 65, False, 0.93),
    # Intel 14th gen
    ("Core i3-14100F", "Intel", "Core i5-14600K", 4700, 4, 0, 8, 58, False, 0.34),
    ("Core i5-14400F", "Intel", "Core i5-14600K", 4700, 10, 6, 16, 65, False, 0.63),
    ("Core i5-14400", "Intel", "Core i5-14600K", 4700, 10, 6, 16, 65, False, 0.72),
    ("Core i5-14500", "Intel", "Core i5-14600K", 5000, 14, 8, 20, 65, False, 0.75),
    ("Core i5-14600", "Intel", "Core i5-14600K", 5200, 14, 8, 20, 65, False, 0.83),
    ("Core i7-14700F", "Intel", "Core i7-14700K", 5400, 20, 12, 28, 65, False, 0.91),
    ("Core i7-14700", "Intel", "Core i7-14700K", 5400, 20, 12, 28, 65, False, 0.94),
    ("Core i9-14900F", "Intel", "Core i9-14900K", 5800, 24, 16, 32, 65, False, 0.89),
    ("Core i9-14900", "Intel", "Core i9-14900K", 5800, 24, 16, 32, 65, False, 0.93),
    ("Core i9-14900KS", "Intel", "Core i9-14900K", 6200, 24, 16, 32, 150, True, 1.17),
    # Intel Core Ultra 200S (LGA 1851)
    ("Core Ultra 9 285", "Intel", "Core Ultra 9 285K", 5600, 24, 16, 24, 65, False, 0.93),
    ("Core Ultra 7 265", "Intel", "Core Ultra 7 265K", 5300, 20, 12, 20, 65, False, 0.97),
    ("Core Ultra 7 265F", "Intel", "Core Ultra 7 265K", 5300, 20, 12, 20, 65, False, 0.94),
    ("Core Ultra 5 235", "Intel", "Core Ultra 5 245K", 5000, 14, 8, 14, 65, False, 0.81),
    ("Core Ultra 5 225", "Intel", "Core Ultra 5 245K", 4900, 10, 4, 10, 65, False, 0.76),
    ("Core Ultra 5 225F", "Intel", "Core Ultra 5 245K", 4900, 10, 4, 10, 65, False, 0.71),
    # AMD AM5
    ("Ryzen 5 7500F", "AMD", "Ryzen 5 7600X", 5000, 6, 0, 12, 65, True, 0.60),
    ("Ryzen 5 7600", "AMD", "Ryzen 5 7600X", 5100, 6, 0, 12, 65, True, 0.77),
    ("Ryzen 7 7700", "AMD", "Ryzen 7 7700X", 5300, 8, 0, 16, 65, True, 0.82),
    ("Ryzen 9 7900", "AMD", "Ryzen 9 7900X", 5400, 12, 0, 24, 65, True, 0.78),
    ("Ryzen 5 8400F", "AMD", "Ryzen 5 7600X", 4700, 6, 0, 12, 65, True, 0.57),
    ("Ryzen 5 8500G", "AMD", "Ryzen 5 7600X", 5000, 6, 0, 12, 65, True, 0.60),
    ("Ryzen 5 8600G", "AMD", "Ryzen 5 7600X", 5000, 6, 0, 12, 65, True, 0.77),
    ("Ryzen 7 8700F", "AMD", "Ryzen 7 7700X", 5000, 8, 0, 16, 65, True, 0.67),
    ("Ryzen 7 8700G", "AMD", "Ryzen 7 7700X", 5100, 8, 0, 16, 65, True, 0.82),
    ("Ryzen 5 9600", "AMD", "Ryzen 5 9600X", 5200, 6, 0, 12, 65, True, 0.82),
    # AMD AM4
    ("Ryzen 5 5500", "AMD", "Ryzen 5 5600X", 4200, 6, 0, 12, 65, True, 0.53),
    ("Ryzen 5 5600", "AMD", "Ryzen 5 5600X", 4400, 6, 0, 12, 65, True, 0.67),
    ("Ryzen 5 5600G", "AMD", "Ryzen 5 5600X", 4400, 6, 0, 12, 65, True, 0.87),
    ("Ryzen 5 5600XT", "AMD", "Ryzen 5 5600X", 4700, 6, 0, 12, 65, True, 0.67),
    ("Ryzen 7 5700X", "AMD", "Ryzen 7 5800X", 4600, 8, 0, 16, 65, True, 0.67),
    ("Ryzen 7 5700G", "AMD", "Ryzen 7 5800X", 4600, 8, 0, 16, 65, True, 0.80),
    ("Ryzen 7 5700X3D", "AMD", "Ryzen 7 5800X3D", 4100, 8, 0, 16, 105, False, 0.55),
    ("Ryzen 7 5800XT", "AMD", "Ryzen 7 5800X", 4800, 8, 0, 16, 105, True, 0.55),
    ("Ryzen 9 5900XT", "AMD", "Ryzen 9 5950X", 4800, 16, 0, 32, 105, True, 0.44),
]

# ---------------------------------------------------------------- Motherboards
ATX, MATX, ITX, EATX = "S-ATX", "Micro-ATX", "Mini-ITX", "E-ATX"
# manufacturer, name, socket, chipset, size, ram, price
MOTHERBOARDS = [
    # AM5
    ("ASUS", "ROG Strix B650E-F Gaming WiFi", "AM5", "B650E", ATX, "DDR5", 280),
    ("ASUS", "TUF Gaming B650-Plus WiFi", "AM5", "B650", ATX, "DDR5", 230),
    ("ASUS", "Prime B650-Plus", "AM5", "B650", ATX, "DDR5", 160),
    ("ASUS", "ROG Strix X670E-E Gaming WiFi", "AM5", "X670E", ATX, "DDR5", 500),
    ("ASUS", "ROG Crosshair X670E Hero", "AM5", "X670E", ATX, "DDR5", 700),
    ("ASUS", "TUF Gaming X870-Plus WiFi", "AM5", "X870", ATX, "DDR5", 310),
    ("ASUS", "ROG Strix X870E-E Gaming WiFi", "AM5", "X870E", ATX, "DDR5", 500),
    ("ASUS", "ROG Strix B850-F Gaming WiFi", "AM5", "B850", ATX, "DDR5", 300),
    ("ASUS", "TUF Gaming B850-Plus WiFi", "AM5", "B850", ATX, "DDR5", 230),
    ("ASUS", "ROG Strix B650E-I Gaming WiFi", "AM5", "B650E", ITX, "DDR5", 330),
    ("ASUS", "TUF Gaming B650M-Plus WiFi", "AM5", "B650", MATX, "DDR5", 190),
    ("ASUS", "Prime B650M-A WiFi II", "AM5", "B650", MATX, "DDR5", 150),
    ("MSI", "MAG B650 Tomahawk WiFi", "AM5", "B650", ATX, "DDR5", 220),
    ("MSI", "MPG B650 Carbon WiFi", "AM5", "B650", ATX, "DDR5", 300),
    ("MSI", "MAG X670E Tomahawk WiFi", "AM5", "X670E", ATX, "DDR5", 280),
    ("MSI", "MPG X670E Carbon WiFi", "AM5", "X670E", ATX, "DDR5", 480),
    ("MSI", "MAG X870 Tomahawk WiFi", "AM5", "X870", ATX, "DDR5", 300),
    ("MSI", "MPG X870E Carbon WiFi", "AM5", "X870E", ATX, "DDR5", 500),
    ("MSI", "MAG B850 Tomahawk MAX WiFi", "AM5", "B850", ATX, "DDR5", 240),
    ("MSI", "PRO B650-P WiFi", "AM5", "B650", ATX, "DDR5", 180),
    ("MSI", "PRO B650M-A WiFi", "AM5", "B650", MATX, "DDR5", 160),
    ("MSI", "MPG B650I Edge WiFi", "AM5", "B650", ITX, "DDR5", 270),
    ("GIGABYTE", "B650 AORUS Elite AX", "AM5", "B650", ATX, "DDR5", 220),
    ("GIGABYTE", "B650 Gaming X AX", "AM5", "B650", ATX, "DDR5", 190),
    ("GIGABYTE", "X670E AORUS Master", "AM5", "X670E", EATX, "DDR5", 500),
    ("GIGABYTE", "X670 AORUS Elite AX", "AM5", "X670", ATX, "DDR5", 290),
    ("GIGABYTE", "X870E AORUS Master", "AM5", "X870E", EATX, "DDR5", 500),
    ("GIGABYTE", "X870 AORUS Elite WiFi7", "AM5", "X870", ATX, "DDR5", 300),
    ("GIGABYTE", "B850 AORUS Elite WiFi7", "AM5", "B850", ATX, "DDR5", 260),
    ("GIGABYTE", "B850 Gaming X WiFi6E", "AM5", "B850", ATX, "DDR5", 200),
    ("GIGABYTE", "B650M AORUS Elite AX", "AM5", "B650", MATX, "DDR5", 200),
    ("GIGABYTE", "B650I AORUS Ultra", "AM5", "B650", ITX, "DDR5", 260),
    ("ASRock", "B650M Pro RS WiFi", "AM5", "B650", MATX, "DDR5", 140),
    ("ASRock", "B650 Steel Legend WiFi", "AM5", "B650", ATX, "DDR5", 220),
    ("ASRock", "B650E PG Riptide WiFi", "AM5", "B650E", ATX, "DDR5", 220),
    ("ASRock", "X670E Taichi", "AM5", "X670E", EATX, "DDR5", 500),
    ("ASRock", "X870 Steel Legend WiFi", "AM5", "X870", ATX, "DDR5", 260),
    ("ASRock", "X870E Taichi", "AM5", "X870E", EATX, "DDR5", 500),
    ("ASRock", "B850M Pro RS WiFi", "AM5", "B850", MATX, "DDR5", 160),
    # LGA 1700
    ("ASUS", "ROG Maximus Z790 Hero", "LGA 1700", "Z790", ATX, "DDR5", 630),
    ("ASUS", "ROG Strix Z790-E Gaming WiFi", "LGA 1700", "Z790", ATX, "DDR5", 480),
    ("ASUS", "ROG Strix Z790-F Gaming WiFi", "LGA 1700", "Z790", ATX, "DDR5", 400),
    ("ASUS", "TUF Gaming Z790-Plus WiFi", "LGA 1700", "Z790", ATX, "DDR5", 290),
    ("ASUS", "Prime Z790-P WiFi", "LGA 1700", "Z790", ATX, "DDR5", 220),
    ("ASUS", "ROG Strix B760-F Gaming WiFi", "LGA 1700", "B760", ATX, "DDR5", 260),
    ("ASUS", "TUF Gaming B760-Plus WiFi D4", "LGA 1700", "B760", ATX, "DDR4", 190),
    ("ASUS", "Prime B760M-A WiFi D4", "LGA 1700", "B760", MATX, "DDR4", 140),
    ("ASUS", "ROG Strix B760-I Gaming WiFi", "LGA 1700", "B760", ITX, "DDR5", 230),
    ("ASUS", "Prime H610M-E D4", "LGA 1700", "H610", MATX, "DDR4", 90),
    ("MSI", "MAG Z790 Tomahawk WiFi", "LGA 1700", "Z790", ATX, "DDR5", 300),
    ("MSI", "MPG Z790 Carbon WiFi", "LGA 1700", "Z790", ATX, "DDR5", 430),
    ("MSI", "PRO Z790-A WiFi", "LGA 1700", "Z790", ATX, "DDR5", 240),
    ("MSI", "MPG Z790I Edge WiFi", "LGA 1700", "Z790", ITX, "DDR5", 380),
    ("MSI", "MAG B760 Tomahawk WiFi", "LGA 1700", "B760", ATX, "DDR5", 220),
    ("MSI", "PRO B760M-A WiFi", "LGA 1700", "B760", MATX, "DDR5", 160),
    ("MSI", "MAG B760M Mortar WiFi", "LGA 1700", "B760", MATX, "DDR5", 200),
    ("MSI", "PRO B760-P DDR4", "LGA 1700", "B760", ATX, "DDR4", 150),
    ("MSI", "PRO H610M-G DDR4", "LGA 1700", "H610", MATX, "DDR4", 90),
    ("GIGABYTE", "Z790 AORUS Elite AX", "LGA 1700", "Z790", ATX, "DDR5", 260),
    ("GIGABYTE", "Z790 AORUS Master", "LGA 1700", "Z790", EATX, "DDR5", 470),
    ("GIGABYTE", "Z790 UD AX", "LGA 1700", "Z790", ATX, "DDR5", 220),
    ("GIGABYTE", "B760 AORUS Elite AX", "LGA 1700", "B760", ATX, "DDR5", 210),
    ("GIGABYTE", "B760 Gaming X AX", "LGA 1700", "B760", ATX, "DDR5", 180),
    ("GIGABYTE", "B760M AORUS Elite AX", "LGA 1700", "B760", MATX, "DDR5", 190),
    ("GIGABYTE", "B760M DS3H DDR4", "LGA 1700", "B760", MATX, "DDR4", 120),
    ("GIGABYTE", "H610M S2H DDR4", "LGA 1700", "H610", MATX, "DDR4", 90),
    ("ASRock", "Z790 Steel Legend WiFi", "LGA 1700", "Z790", ATX, "DDR5", 260),
    ("ASRock", "Z790 Taichi", "LGA 1700", "Z790", EATX, "DDR5", 500),
    ("ASRock", "Z790 PG Lightning", "LGA 1700", "Z790", ATX, "DDR5", 200),
    ("ASRock", "Z790I Lightning WiFi", "LGA 1700", "Z790", ITX, "DDR5", 230),
    ("ASRock", "B760 Pro RS", "LGA 1700", "B760", ATX, "DDR5", 150),
    ("ASRock", "B760M Pro RS", "LGA 1700", "B760", MATX, "DDR5", 130),
    # LGA 1851
    ("ASUS", "ROG Maximus Z890 Hero", "LGA 1851", "Z890", ATX, "DDR5", 650),
    ("ASUS", "ROG Strix Z890-E Gaming WiFi", "LGA 1851", "Z890", ATX, "DDR5", 500),
    ("ASUS", "ROG Strix Z890-F Gaming WiFi", "LGA 1851", "Z890", ATX, "DDR5", 430),
    ("ASUS", "TUF Gaming Z890-Plus WiFi", "LGA 1851", "Z890", ATX, "DDR5", 330),
    ("ASUS", "Prime Z890-P WiFi", "LGA 1851", "Z890", ATX, "DDR5", 250),
    ("ASUS", "ROG Strix B860-F Gaming WiFi", "LGA 1851", "B860", ATX, "DDR5", 290),
    ("ASUS", "TUF Gaming B860-Plus WiFi", "LGA 1851", "B860", ATX, "DDR5", 220),
    ("ASUS", "Prime B860M-A WiFi", "LGA 1851", "B860", MATX, "DDR5", 170),
    ("MSI", "MAG Z890 Tomahawk WiFi", "LGA 1851", "Z890", ATX, "DDR5", 330),
    ("MSI", "MPG Z890 Carbon WiFi", "LGA 1851", "Z890", ATX, "DDR5", 500),
    ("MSI", "PRO Z890-A WiFi", "LGA 1851", "Z890", ATX, "DDR5", 260),
    ("MSI", "MAG B860 Tomahawk WiFi", "LGA 1851", "B860", ATX, "DDR5", 230),
    ("MSI", "PRO B860M-A WiFi", "LGA 1851", "B860", MATX, "DDR5", 170),
    ("GIGABYTE", "Z890 AORUS Elite WiFi7", "LGA 1851", "Z890", ATX, "DDR5", 300),
    ("GIGABYTE", "Z890 AORUS Master", "LGA 1851", "Z890", EATX, "DDR5", 500),
    ("GIGABYTE", "Z890 Eagle WiFi7", "LGA 1851", "Z890", ATX, "DDR5", 250),
    ("GIGABYTE", "B860 AORUS Elite WiFi6E", "LGA 1851", "B860", ATX, "DDR5", 220),
    ("GIGABYTE", "B860M Gaming X WiFi6E", "LGA 1851", "B860", MATX, "DDR5", 170),
    ("ASRock", "Z890 Steel Legend WiFi", "LGA 1851", "Z890", ATX, "DDR5", 280),
    ("ASRock", "Z890 Taichi", "LGA 1851", "Z890", EATX, "DDR5", 530),
    ("ASRock", "Z890 Pro RS WiFi", "LGA 1851", "Z890", ATX, "DDR5", 240),
    ("ASRock", "B860M Pro RS WiFi", "LGA 1851", "B860", MATX, "DDR5", 150),
    # AM4
    ("ASUS", "ROG Strix B550-F Gaming WiFi", "AM4", "B550", ATX, "DDR4", 190),
    ("ASUS", "TUF Gaming B550-Plus", "AM4", "B550", ATX, "DDR4", 150),
    ("ASUS", "TUF Gaming X570-Plus WiFi", "AM4", "X570", ATX, "DDR4", 200),
    ("ASUS", "Prime B550M-A WiFi", "AM4", "B550", MATX, "DDR4", 130),
    ("ASUS", "ROG Strix B550-I Gaming", "AM4", "B550", ITX, "DDR4", 220),
    ("MSI", "MAG B550 Tomahawk", "AM4", "B550", ATX, "DDR4", 180),
    ("MSI", "B550 Gaming Plus", "AM4", "B550", ATX, "DDR4", 140),
    ("MSI", "MPG X570 Gaming Plus", "AM4", "X570", ATX, "DDR4", 160),
    ("MSI", "B450 Tomahawk MAX", "AM4", "B450", ATX, "DDR4", 115),
    ("MSI", "A520M-A PRO", "AM4", "A520", MATX, "DDR4", 75),
    ("GIGABYTE", "B550 AORUS Elite V2", "AM4", "B550", ATX, "DDR4", 170),
    ("GIGABYTE", "B550M DS3H", "AM4", "B550", MATX, "DDR4", 100),
    ("GIGABYTE", "X570 AORUS Elite", "AM4", "X570", ATX, "DDR4", 200),
    ("GIGABYTE", "B450 AORUS M", "AM4", "B450", MATX, "DDR4", 90),
    ("ASRock", "B550 Steel Legend", "AM4", "B550", ATX, "DDR4", 170),
    ("ASRock", "B550M Pro4", "AM4", "B550", MATX, "DDR4", 115),
    ("ASRock", "X570 Steel Legend", "AM4", "X570", ATX, "DDR4", 190),
    ("ASRock", "B450M Pro4", "AM4", "B450", MATX, "DDR4", 80),
    ("ASRock", "A520M-HDV", "AM4", "A520", MATX, "DDR4", 60),
]
# Chipsets that cannot overclock the CPU.
LOCKED_CHIPSETS = {"B760", "H610", "B860", "A520"}

# ---------------------------------------------------------------- RAM (single sticks, like stock)
# manufacturer, line, type, MHz, CAS, volts, sizes, lighting, price tier (1.0 base)
RAM = [
    ("CORSAIR", "Vengeance RGB DDR5", "DDR5", 6000, 30, 1.35, [16, 32], "RGB", 1.1),
    ("CORSAIR", "Vengeance RGB DDR5", "DDR5", 6400, 32, 1.40, [16, 32], "RGB", 1.15),
    ("CORSAIR", "Vengeance DDR5", "DDR5", 5600, 36, 1.25, [16, 32], "N/A", 1.0),
    ("CORSAIR", "Dominator Titanium RGB DDR5", "DDR5", 6600, 32, 1.40, [16, 32], "RGB", 1.35),
    ("CORSAIR", "Vengeance LPX DDR4", "DDR4", 3200, 16, 1.35, [8, 16, 32], "N/A", 1.0),
    ("CORSAIR", "Vengeance RGB Pro DDR4", "DDR4", 3600, 18, 1.35, [8, 16, 32], "RGB", 1.15),
    ("G.SKILL", "Trident Z5 RGB", "DDR5", 6000, 30, 1.35, [16, 32], "RGB", 1.15),
    ("G.SKILL", "Trident Z5 RGB", "DDR5", 6400, 32, 1.40, [16, 32], "RGB", 1.2),
    ("G.SKILL", "Trident Z5 Neo RGB", "DDR5", 6000, 30, 1.35, [16, 32], "RGB", 1.15),
    ("G.SKILL", "Flare X5", "DDR5", 6000, 30, 1.35, [16, 32], "N/A", 1.05),
    ("G.SKILL", "Ripjaws S5", "DDR5", 6000, 30, 1.35, [16, 32], "N/A", 1.0),
    ("G.SKILL", "Ripjaws S5", "DDR5", 5200, 36, 1.20, [16, 32], "N/A", 0.95),
    ("G.SKILL", "Ripjaws V DDR4", "DDR4", 3600, 16, 1.35, [8, 16, 32], "N/A", 1.0),
    ("G.SKILL", "Trident Z Neo DDR4", "DDR4", 3600, 16, 1.35, [8, 16, 32], "RGB", 1.2),
    ("Kingston", "FURY Beast DDR5 RGB", "DDR5", 6000, 30, 1.35, [16, 32], "RGB", 1.1),
    ("Kingston", "FURY Beast DDR5", "DDR5", 5600, 40, 1.25, [16, 32], "N/A", 0.95),
    ("Kingston", "FURY Renegade DDR5 RGB", "DDR5", 6400, 32, 1.40, [16, 32], "RGB", 1.25),
    ("Kingston", "FURY Beast DDR4", "DDR4", 3200, 16, 1.35, [8, 16, 32], "N/A", 1.0),
    ("Kingston", "FURY Renegade DDR4", "DDR4", 3600, 16, 1.35, [8, 16, 32], "N/A", 1.15),
    ("Team Group", "T-Force Delta RGB DDR5 (Black)", "DDR5", 6000, 30, 1.35, [16, 32], "RGB", 1.05),
    ("Team Group", "T-Force Delta RGB DDR5 (White)", "DDR5", 6000, 30, 1.35, [16, 32], "RGB", 1.05),
    ("Team Group", "T-Create Expert DDR5", "DDR5", 6000, 30, 1.35, [16, 32], "N/A", 1.0),
    ("Team Group", "T-Force Vulcan Z DDR4", "DDR4", 3200, 16, 1.35, [8, 16], "N/A", 0.95),
    ("ADATA", "XPG Lancer RGB DDR5", "DDR5", 6000, 30, 1.35, [16, 32], "RGB", 1.05),
    ("ADATA", "XPG Lancer Blade RGB DDR5", "DDR5", 6000, 30, 1.35, [16, 24], "RGB", 1.05),
    ("Patriot", "Viper Venom RGB DDR5", "DDR5", 6400, 32, 1.40, [16, 32], "RGB", 1.1),
    ("Patriot", "Viper Xtreme 5 RGB DDR5", "DDR5", 7600, 36, 1.45, [24], "RGB", 1.4),
    ("Patriot", "Viper Steel DDR4", "DDR4", 3600, 18, 1.35, [8, 16], "N/A", 1.0),
    ("Crucial", "Pro DDR5", "DDR5", 5600, 46, 1.10, [16, 24, 32], "N/A", 0.9),
    ("Crucial", "Pro OC DDR5", "DDR5", 6000, 36, 1.35, [16, 32], "N/A", 1.0),
    ("Crucial", "Ballistix DDR4", "DDR4", 3600, 16, 1.35, [8, 16], "N/A", 1.0),
]

# ---------------------------------------------------------------- Storage
# manufacturer, line, type (M2 / SSD / HDD), read MB/s, sizes GB, $ per TB, heatsink
STORAGE = [
    ("Samsung", "990 PRO NVMe M.2 SSD", "M2", 7450, [1000, 2000, 4000], 95, False),
    ("Samsung", "990 PRO NVMe M.2 SSD with Heatsink", "M2", 7450, [1000, 2000, 4000], 110, True),
    ("Samsung", "990 EVO Plus NVMe M.2 SSD", "M2", 7250, [1000, 2000, 4000], 75, False),
    ("Samsung", "9100 PRO NVMe M.2 SSD", "M2", 14700, [1000, 2000, 4000], 160, False),
    ("Samsung", "980 PRO NVMe M.2 SSD", "M2", 7000, [500, 1000, 2000], 85, False),
    ("Samsung", "970 EVO Plus NVMe M.2 SSD", "M2", 3500, [500, 1000, 2000], 70, False),
    ("Samsung", "870 EVO SATA SSD", "SSD", 560, [500, 1000, 2000, 4000], 70, False),
    ("WD", "Black SN850X NVMe SSD", "M2", 7300, [1000, 2000, 4000], 85, False),
    ("WD", "Black SN850X NVMe SSD with Heatsink", "M2", 7300, [1000, 2000, 4000], 100, True),
    ("WD", "Black SN8100 NVMe SSD", "M2", 14900, [1000, 2000, 4000], 150, False),
    ("WD", "Black SN770 NVMe SSD", "M2", 5150, [500, 1000, 2000], 65, False),
    ("WD", "Blue SN5000 NVMe SSD", "M2", 5500, [500, 1000, 2000, 4000], 60, False),
    ("WD", "Blue SA510 SATA SSD", "SSD", 560, [500, 1000, 2000], 60, False),
    ("WD", "Blue 7200 RPM HDD", "HDD", 215, [1000, 2000, 4000], 20, False),
    ("WD", "Black Performance HDD", "HDD", 250, [2000, 4000, 8000], 28, False),
    ("Seagate", "BarraCuda HDD", "HDD", 220, [2000, 4000, 8000], 18, False),
    ("Seagate", "IronWolf Pro HDD", "HDD", 285, [8000, 12000, 16000], 22, False),
    ("Seagate", "FireCuda 530 NVMe SSD", "M2", 7300, [500, 1000, 2000, 4000], 95, False),
    ("Seagate", "FireCuda 540 NVMe SSD", "M2", 10000, [1000, 2000], 140, False),
    ("Crucial", "T705 Gen5 NVMe SSD", "M2", 14500, [1000, 2000, 4000], 155, False),
    ("Crucial", "T700 Gen5 NVMe SSD", "M2", 12400, [1000, 2000, 4000], 130, False),
    ("Crucial", "T500 NVMe SSD", "M2", 7400, [500, 1000, 2000], 70, False),
    ("Crucial", "P310 NVMe SSD", "M2", 7100, [500, 1000, 2000], 60, False),
    ("Crucial", "P3 Plus NVMe SSD", "M2", 5000, [500, 1000, 2000, 4000], 55, False),
    ("Crucial", "MX500 SATA SSD", "SSD", 560, [500, 1000, 2000, 4000], 60, False),
    ("Kingston", "KC3000 NVMe SSD", "M2", 7000, [512, 1024, 2048, 4096], 80, False),
    ("Kingston", "NV3 NVMe SSD", "M2", 6000, [500, 1000, 2000, 4000], 55, False),
    ("Kingston", "FURY Renegade NVMe SSD", "M2", 7300, [500, 1000, 2000, 4000], 90, False),
    ("SK hynix", "Platinum P41 NVMe SSD", "M2", 7000, [500, 1000, 2000], 85, False),
    ("Solidigm", "P44 Pro NVMe SSD", "M2", 7000, [512, 1024, 2048], 75, False),
    ("CORSAIR", "MP600 PRO LPX NVMe SSD", "M2", 7100, [1000, 2000, 4000], 85, False),
    ("CORSAIR", "MP700 PRO Gen5 NVMe SSD", "M2", 12400, [1000, 2000, 4000], 140, False),
    ("Lexar", "NM790 NVMe SSD", "M2", 7400, [1000, 2000, 4000], 65, False),
    ("Team Group", "T-Force Cardea Z44Q NVMe SSD", "M2", 7400, [1000, 2000, 4000], 70, False),
    ("ADATA", "XPG GAMMIX S70 Blade NVMe SSD", "M2", 7400, [1000, 2000, 4000], 75, False),
]

# ---------------------------------------------------------------- PSUs
# manufacturer, name, watts, size (ATX/SFX), modularity (Modular/None), price
PSUS = [
    ("CORSAIR", "RM750e", 750, "ATX", "Modular", 100), ("CORSAIR", "RM850e", 850, "ATX", "Modular", 115),
    ("CORSAIR", "RM850x", 850, "ATX", "Modular", 150), ("CORSAIR", "RM1000x", 1000, "ATX", "Modular", 190),
    ("CORSAIR", "RM1200x Shift", 1200, "ATX", "Modular", 230), ("CORSAIR", "HX1000i", 1000, "ATX", "Modular", 250),
    ("CORSAIR", "HX1500i", 1500, "ATX", "Modular", 400), ("CORSAIR", "SF750", 750, "SFX", "Modular", 185),
    ("CORSAIR", "SF1000", 1000, "SFX", "Modular", 240), ("CORSAIR", "CX650", 650, "ATX", "None", 70),
    ("Seasonic", "Focus GX-750", 750, "ATX", "Modular", 130), ("Seasonic", "Focus GX-850", 850, "ATX", "Modular", 140),
    ("Seasonic", "Focus GX-1000", 1000, "ATX", "Modular", 180), ("Seasonic", "Vertex GX-1200", 1200, "ATX", "Modular", 230),
    ("Seasonic", "Prime TX-1000", 1000, "ATX", "Modular", 330), ("Seasonic", "Prime TX-1600", 1600, "ATX", "Modular", 520),
    ("Seasonic", "Focus SGX-650", 650, "SFX", "Modular", 140),
    ("be quiet!", "Pure Power 12 M 750W", 750, "ATX", "Modular", 110), ("be quiet!", "Pure Power 12 M 850W", 850, "ATX", "Modular", 125),
    ("be quiet!", "Straight Power 12 1000W", 1000, "ATX", "Modular", 230), ("be quiet!", "Dark Power 13 1000W", 1000, "ATX", "Modular", 290),
    ("be quiet!", "Dark Power Pro 13 1600W", 1600, "ATX", "Modular", 450), ("be quiet!", "SFX L Power 600W", 600, "SFX", "Modular", 140),
    ("MSI", "MAG A750GL PCIE5", 750, "ATX", "Modular", 100), ("MSI", "MAG A1000GL PCIE5", 1000, "ATX", "Modular", 160),
    ("Cooler Master", "MWE Gold 750 V2", 750, "ATX", "Modular", 100), ("Cooler Master", "MWE Gold 850 V2", 850, "ATX", "Modular", 115),
    ("Cooler Master", "V850 SFX Gold", 850, "SFX", "Modular", 160),
    ("Lian Li", "SP750", 750, "SFX", "Modular", 140),
    ("NZXT", "C750 Bronze", 750, "ATX", "None", 90), ("NZXT", "C850 Gold", 850, "ATX", "Modular", 130),
    ("NZXT", "C1200 Gold", 1200, "ATX", "Modular", 200),
    ("ASUS", "ROG Thor 1000P2", 1000, "ATX", "Modular", 330), ("ASUS", "ROG Thor 1200P2", 1200, "ATX", "Modular", 380),
    ("ASUS", "TUF Gaming 850G", 850, "ATX", "Modular", 140), ("ASUS", "TUF Gaming 1000G", 1000, "ATX", "Modular", 180),
    ("ASUS", "ROG Loki SFX-L 850W", 850, "SFX", "Modular", 220),
    ("Thermaltake", "Toughpower GF3 850W", 850, "ATX", "Modular", 140), ("Thermaltake", "Toughpower GF3 1000W", 1000, "ATX", "Modular", 170),
    ("Thermaltake", "Smart BX1 650W", 650, "ATX", "None", 65),
    ("EVGA", "SuperNOVA 850 G7", 850, "ATX", "Modular", 150), ("EVGA", "SuperNOVA 1000 G7", 1000, "ATX", "Modular", 190),
    ("Super Flower", "Leadex VII XG 1000W", 1000, "ATX", "Modular", 210), ("Super Flower", "Leadex III Gold 850W", 850, "ATX", "Modular", 130),
    ("FSP", "Hydro G Pro 850W", 850, "ATX", "Modular", 140), ("FSP", "Hydro Ti Pro 1000W", 1000, "ATX", "Modular", 230),
]

# ---------------------------------------------------------------- CPU coolers
# Air: manufacturer, name, height mm, price, lighting
AIR_COOLERS = [
    ("Noctua", "NH-D15 G2", 168, 150, "N/A"), ("Noctua", "NH-D15 chromax.black", 165, 120, "N/A"),
    ("Noctua", "NH-U12A", 158, 100, "N/A"), ("Noctua", "NH-U12S redux", 158, 50, "N/A"),
    ("Noctua", "NH-U14S", 165, 80, "N/A"),
    ("Thermalright", "Peerless Assassin 120 SE", 155, 35, "N/A"), ("Thermalright", "Phantom Spirit 120 SE", 154, 40, "ARGB"),
    ("Thermalright", "Assassin X 120 Refined SE", 148, 20, "N/A"),
    ("Deepcool", "AK400", 155, 35, "N/A"), ("Deepcool", "AK500", 158, 55, "N/A"),
    ("Deepcool", "AK620", 160, 65, "N/A"), ("Deepcool", "AG400", 150, 25, "N/A"),
    ("be quiet!", "Dark Rock Pro 5", 168, 100, "N/A"), ("be quiet!", "Dark Rock 5", 161, 75, "N/A"),
    ("be quiet!", "Pure Rock 2", 155, 45, "N/A"),
    ("ARCTIC", "Freezer 36", 159, 30, "N/A"), ("Scythe", "Fuma 3", 155, 60, "N/A"),
    ("Cooler Master", "Hyper 212 Black Edition", 159, 30, "N/A"), ("Cooler Master", "Hyper 212 Halo", 154, 40, "ARGB"),
    ("ID-COOLING", "SE-224-XTS", 154, 20, "N/A"), ("CORSAIR", "A115", 169, 100, "N/A"),
]
# Liquid: manufacturer, name, fan size, fan count, price, lighting
LIQUID_COOLERS = [
    ("ARCTIC", "Liquid Freezer III 240", 120, 2, 80, "N/A"), ("ARCTIC", "Liquid Freezer III 280", 140, 2, 90, "N/A"),
    ("ARCTIC", "Liquid Freezer III 360", 120, 3, 100, "N/A"), ("ARCTIC", "Liquid Freezer III 420", 140, 3, 120, "N/A"),
    ("ARCTIC", "Liquid Freezer III 360 A-RGB", 120, 3, 110, "ARGB"),
    ("NZXT", "Kraken 240", 120, 2, 140, "RGB"), ("NZXT", "Kraken 280", 140, 2, 160, "RGB"),
    ("NZXT", "Kraken 360", 120, 3, 180, "RGB"), ("NZXT", "Kraken Elite 360", 120, 3, 280, "RGB"),
    ("CORSAIR", "iCUE H150i Elite LCD XT", 120, 3, 260, "RGB"), ("CORSAIR", "iCUE LINK H150i RGB", 120, 3, 220, "RGB"),
    ("CORSAIR", "iCUE LINK H100i RGB", 120, 2, 170, "RGB"), ("CORSAIR", "Nautilus 360 RS", 120, 3, 110, "N/A"),
    ("Lian Li", "Galahad II Trinity 360", 120, 3, 150, "ARGB"), ("Lian Li", "HydroShift LCD 360S", 120, 3, 200, "ARGB"),
    ("Deepcool", "LT720", 120, 3, 120, "ARGB"), ("Deepcool", "LS720", 120, 3, 130, "ARGB"),
    ("Thermalright", "Frozen Notte 360", 120, 3, 70, "ARGB"), ("Thermalright", "Aqua Elite 360 V3", 120, 3, 60, "ARGB"),
    ("be quiet!", "Pure Loop 2 360", 120, 3, 120, "ARGB"), ("be quiet!", "Silent Loop 3 360", 120, 3, 160, "ARGB"),
    ("be quiet!", "Light Loop 360", 120, 3, 190, "ARGB"),
    ("Cooler Master", "MasterLiquid 360L Core ARGB", 120, 3, 90, "ARGB"), ("MSI", "MAG CoreLiquid A13 360", 120, 3, 90, "ARGB"),
    ("EKWB", "EK-Nucleus AIO CR360 Lux D-RGB", 120, 3, 150, "ARGB"),
    ("ASUS", "ROG Ryujin III 360 ARGB", 120, 3, 330, "ARGB"), ("ASUS", "ROG Strix LC III 360 ARGB", 120, 3, 220, "ARGB"),
    ("ASUS", "TUF Gaming LC II 360 ARGB", 120, 3, 150, "ARGB"), ("ASUS", "ROG Ryujin III 240 ARGB", 120, 2, 280, "ARGB"),
]

# ---------------------------------------------------------------- Cases
# manufacturer, name, max board, case size, price
CASES = [
    ("Lian Li", "O11 Dynamic EVO", EATX, "Mid Tower", 160), ("Lian Li", "O11 Dynamic EVO RGB", EATX, "Mid Tower", 190),
    ("Lian Li", "O11 Vision", EATX, "Mid Tower", 150), ("Lian Li", "O11 Dynamic Mini V2", ATX, "Mid Tower", 110),
    ("Lian Li", "LANCOOL 216", EATX, "Mid Tower", 100), ("Lian Li", "LANCOOL 207", ATX, "Mid Tower", 85),
    ("Lian Li", "LANCOOL III", EATX, "Full Tower", 150), ("Lian Li", "A3-mATX", MATX, "Micro", 70),
    ("NZXT", "H5 Flow", ATX, "Mid Tower", 95), ("NZXT", "H6 Flow", ATX, "Mid Tower", 115),
    ("NZXT", "H7 Flow", EATX, "Mid Tower", 130), ("NZXT", "H9 Flow", EATX, "Mid Tower", 160),
    ("NZXT", "H9 Elite", EATX, "Mid Tower", 240),
    ("Fractal Design", "North", ATX, "Mid Tower", 140), ("Fractal Design", "North XL", EATX, "Full Tower", 170),
    ("Fractal Design", "Meshify 2", EATX, "Mid Tower", 150), ("Fractal Design", "Meshify 2 Compact", ATX, "Mid Tower", 110),
    ("Fractal Design", "Torrent", EATX, "Mid Tower", 190), ("Fractal Design", "Pop Air", ATX, "Mid Tower", 80),
    ("Fractal Design", "Define 7", EATX, "Mid Tower", 170), ("Fractal Design", "Terra", ITX, "Cube", 180),
    ("CORSAIR", "4000D Airflow", ATX, "Mid Tower", 105), ("CORSAIR", "5000D Airflow", EATX, "Mid Tower", 175),
    ("CORSAIR", "3500X", ATX, "Mid Tower", 100), ("CORSAIR", "6500X", EATX, "Mid Tower", 200),
    ("CORSAIR", "2500X", MATX, "Micro", 110), ("CORSAIR", "iCUE 5000T RGB", EATX, "Mid Tower", 300),
    ("CORSAIR", "FRAME 4000D", ATX, "Mid Tower", 105), ("CORSAIR", "7000D Airflow", EATX, "Full Tower", 230),
    ("HYTE", "Y40", ATX, "Mid Tower", 150), ("HYTE", "Y60", ATX, "Mid Tower", 200), ("HYTE", "Y70", EATX, "Mid Tower", 250),
    ("Phanteks", "NV7", EATX, "Full Tower", 210), ("Phanteks", "NV5", ATX, "Mid Tower", 100),
    ("Phanteks", "XT Pro Ultra", ATX, "Mid Tower", 90), ("Phanteks", "Eclipse G360A", ATX, "Mid Tower", 100),
    ("Phanteks", "Evolv X2", EATX, "Mid Tower", 180),
    ("be quiet!", "Pure Base 500DX", ATX, "Mid Tower", 110), ("be quiet!", "Light Base 900 DX", EATX, "Full Tower", 260),
    ("be quiet!", "Shadow Base 800 DX", EATX, "Mid Tower", 200), ("be quiet!", "Silent Base 802", EATX, "Mid Tower", 180),
    ("Montech", "AIR 903 MAX", EATX, "Mid Tower", 90), ("Montech", "KING 95 PRO", EATX, "Mid Tower", 150),
    ("Montech", "SKY TWO", ATX, "Mid Tower", 110),
    ("Cooler Master", "MasterBox TD500 Mesh V2", ATX, "Mid Tower", 110), ("Cooler Master", "MasterBox Q300L", MATX, "Micro", 50),
    ("Cooler Master", "MasterBox NR200P", ITX, "Micro", 90),
    ("Antec", "C8", EATX, "Full Tower", 110), ("Antec", "Flux Pro", EATX, "Full Tower", 160),
    ("Thermaltake", "Tower 300", MATX, "Micro", 160),
]

# ---------------------------------------------------------------- Case fans
# manufacturer, name, size, CFM, static pressure mmH2O, price, lighting
FANS = [
    ("Noctua", "NF-A12x25 PWM", 120, 60.1, 2.34, 33, "N/A"), ("Noctua", "NF-A12x25 PWM chromax.black", 120, 60.1, 2.34, 35, "N/A"),
    ("Noctua", "NF-A14 PWM", 140, 82.5, 2.08, 25, "N/A"), ("Noctua", "NF-P12 redux-1700 PWM", 120, 70.7, 2.83, 14, "N/A"),
    ("ARCTIC", "P12 Pro PST", 120, 77.0, 6.9, 12, "N/A"), ("ARCTIC", "P14 Pro PST", 140, 90.0, 5.3, 14, "N/A"),
    ("Lian Li", "UNI FAN SL-INF 120", 120, 61.3, 2.66, 30, "ARGB"), ("Lian Li", "UNI FAN TL 120", 120, 69.0, 3.0, 30, "ARGB"),
    ("Lian Li", "UNI FAN SL120 V2", 120, 71.0, 3.2, 25, "ARGB"), ("Lian Li", "UNI FAN SL140 V2", 140, 85.0, 2.7, 30, "ARGB"),
    ("CORSAIR", "iCUE LINK RX120 RGB", 120, 73.5, 4.33, 30, "RGB"), ("CORSAIR", "iCUE LINK QX120 RGB", 120, 63.1, 4.1, 40, "RGB"),
    ("CORSAIR", "iCUE LINK RX140 RGB", 140, 82.0, 3.5, 35, "RGB"), ("CORSAIR", "AF120 RGB Elite", 120, 65.6, 1.95, 20, "RGB"),
    ("be quiet!", "Silent Wings 4 120mm PWM", 120, 48.7, 2.75, 25, "N/A"), ("be quiet!", "Silent Wings 4 140mm PWM", 140, 68.9, 2.07, 27, "N/A"),
    ("be quiet!", "Light Wings 120mm PWM", 120, 51.3, 1.89, 20, "ARGB"), ("be quiet!", "Pure Wings 3 120mm PWM", 120, 52.0, 1.9, 10, "N/A"),
    ("Phanteks", "T30-120", 120, 70.0, 4.65, 33, "N/A"), ("Phanteks", "M25-120 Gen2", 120, 64.0, 2.9, 15, "ARGB"),
    ("Thermalright", "TL-C12C", 120, 66.2, 1.53, 6, "N/A"),
    ("NZXT", "F120 RGB Core", 120, 65.0, 2.6, 25, "RGB"), ("NZXT", "F140 RGB Core", 140, 70.0, 2.2, 30, "RGB"),
    ("NZXT", "F120Q", 120, 50.0, 1.3, 20, "N/A"),
    ("Cooler Master", "MasterFan MF120 Halo2", 120, 47.2, 1.6, 20, "ARGB"), ("Cooler Master", "Mobius 120", 120, 62.0, 3.7, 20, "N/A"),
    ("Fractal Design", "Aspect 12", 120, 45.0, 1.2, 10, "N/A"), ("Fractal Design", "Aspect 14", 140, 68.0, 1.4, 12, "N/A"),
    ("Fractal Design", "Prisma AL-12", 120, 47.0, 1.4, 15, "ARGB"), ("Deepcool", "FC120", 120, 61.9, 2.0, 10, "ARGB"),
]


# ================================================================ Batch 2: older generations
NV30 = ["GeForce RTX 3050", "GeForce RTX 3060", "GeForce RTX 3060 Ti", "GeForce RTX 3070", "GeForce RTX 3070 Ti",
        "GeForce RTX 3080", "GeForce RTX 3080 Ti", "GeForce RTX 3090", "GeForce RTX 3090 Ti"]
GTX16 = ["GeForce GTX 1650", "GeForce GTX 1660 Super", "GeForce GTX 1660 Ti"]
RX6 = ["Radeon RX 6500 XT", "Radeon RX 6800", "Radeon RX 6800 XT", "Radeon RX 6900 XT", "Radeon RX 6950 XT"]

GPU_LINES += [
    ("ASUS", "Dual {c} OC", 0, span(NV30, "GeForce RTX 3050", "GeForce RTX 3070") + GTX16),
    ("ASUS", "TUF Gaming {c} OC", 1, span(NV30, "GeForce RTX 3060", "GeForce RTX 3090 Ti") + GTX16 + span(RX6, "Radeon RX 6800", "Radeon RX 6950 XT")),
    ("ASUS", "ROG Strix {c} OC", 2, span(NV30, "GeForce RTX 3060", "GeForce RTX 3090 Ti") + span(RX6, "Radeon RX 6800 XT", "Radeon RX 6950 XT")),
    ("MSI", "{c} Ventus 2X OC", 0, span(NV30, "GeForce RTX 3050", "GeForce RTX 3070") + GTX16),
    ("MSI", "{c} Ventus 3X OC", 0, span(NV30, "GeForce RTX 3060 Ti", "GeForce RTX 3090")),
    ("MSI", "{c} Gaming X Trio", 1, span(NV30, "GeForce RTX 3060 Ti", "GeForce RTX 3090 Ti") + span(RX6, "Radeon RX 6800", "Radeon RX 6950 XT")),
    ("MSI", "{c} Gaming X", 1, ["GeForce RTX 3050", "GeForce RTX 3060"] + GTX16),
    ("MSI", "{c} Suprim X", 2, span(NV30, "GeForce RTX 3070", "GeForce RTX 3090 Ti")),
    ("MSI", "{c} Mech 2X OC", 0, ["Radeon RX 6500 XT"]),
    ("GIGABYTE", "{c} Eagle OC", 0, NV30 + ["Radeon RX 6500 XT"]),
    ("GIGABYTE", "{c} Gaming OC", 1, NV30 + GTX16 + RX6),
    ("GIGABYTE", "{c} Vision OC", 1, span(NV30, "GeForce RTX 3060", "GeForce RTX 3090")),
    ("GIGABYTE", "AORUS {c} Master", 2, span(NV30, "GeForce RTX 3070", "GeForce RTX 3090") + ["Radeon RX 6800 XT", "Radeon RX 6900 XT"]),
    ("ZOTAC", "Gaming {c} Twin Edge OC", 0, span(NV30, "GeForce RTX 3050", "GeForce RTX 3070 Ti") + GTX16),
    ("ZOTAC", "Gaming {c} Trinity OC", 1, span(NV30, "GeForce RTX 3070 Ti", "GeForce RTX 3090 Ti")),
    ("ZOTAC", "Gaming {c} AMP Holo", 2, span(NV30, "GeForce RTX 3060 Ti", "GeForce RTX 3080 Ti")),
    ("EVGA", "{c} XC Gaming", 0, NV30 + GTX16),
    ("EVGA", "{c} FTW3 Ultra Gaming", 2, span(NV30, "GeForce RTX 3060", "GeForce RTX 3090 Ti")),
    ("PNY", "{c} XLR8 Gaming REVEL EPIC-X RGB", 1, span(NV30, "GeForce RTX 3050", "GeForce RTX 3090")),
    ("Palit", "{c} Dual OC", 0, span(NV30, "GeForce RTX 3050", "GeForce RTX 3070") + GTX16),
    ("Palit", "{c} GamingPro", 1, span(NV30, "GeForce RTX 3060", "GeForce RTX 3090 Ti")),
    ("Palit", "{c} GameRock OC", 2, span(NV30, "GeForce RTX 3070", "GeForce RTX 3090 Ti")),
    ("Gainward", "{c} Ghost", 0, span(NV30, "GeForce RTX 3050", "GeForce RTX 3070")),
    ("Gainward", "{c} Phoenix", 1, span(NV30, "GeForce RTX 3060", "GeForce RTX 3090")),
    ("Sapphire", "PULSE {c}", 0, RX6),
    ("Sapphire", "NITRO+ {c}", 2, RX6),
    ("PowerColor", "Fighter {c}", 0, ["Radeon RX 6500 XT", "Radeon RX 6800"]),
    ("PowerColor", "Red Dragon {c}", 1, span(RX6, "Radeon RX 6800", "Radeon RX 6900 XT")),
    ("PowerColor", "Red Devil {c}", 2, RX6),
    ("XFX", "Speedster SWFT 210 {c}", 0, ["Radeon RX 6500 XT"]),
    ("XFX", "Speedster MERC 319 {c}", 2, span(RX6, "Radeon RX 6800", "Radeon RX 6950 XT")),
    ("ASRock", "{c} Phantom Gaming D OC", 2, span(RX6, "Radeon RX 6800", "Radeon RX 6950 XT")),
    ("ASRock", "{c} Challenger ITX", 0, ["Radeon RX 6500 XT"]),
]

CPUS += [
    # Intel 9th gen (LGA 1151 Coffee Lake)
    ("Core i3-9100F", "Intel", "Core i3-8100", 4200, 4, 0, 4, 65, False, 0.75),
    ("Core i5-9400F", "Intel", "Core i5-8400", 4100, 6, 0, 6, 65, False, 0.80),
    ("Core i5-9600KF", "Intel", "Core i5-9600K", 4600, 6, 0, 6, 95, True, 0.92),
    ("Core i7-9700F", "Intel", "Core i7-9700K", 4700, 8, 0, 8, 65, False, 0.83),
    ("Core i7-9700KF", "Intel", "Core i7-9700K", 4900, 8, 0, 8, 95, True, 0.95),
    ("Core i9-9900KF", "Intel", "Core i9-9900K", 5000, 8, 0, 16, 95, True, 0.95),
    ("Core i9-9900KS", "Intel", "Core i9-9900K", 5000, 8, 0, 16, 127, True, 1.05),
    # Intel 10th/11th gen (LGA 1200)
    ("Core i3-10105F", "Intel", "Core i3-10100", 4400, 4, 0, 8, 65, False, 0.80),
    ("Core i3-10105", "Intel", "Core i3-10100", 4400, 4, 0, 8, 65, False, 0.95),
    ("Core i5-10400F", "Intel", "Core i5-10400", 4300, 6, 0, 12, 65, False, 0.85),
    ("Core i5-10600KF", "Intel", "Core i5-10600K", 4800, 6, 0, 12, 125, True, 0.93),
    ("Core i7-10700F", "Intel", "Core i7-10700", 4800, 8, 0, 16, 65, False, 0.92),
    ("Core i7-10700KF", "Intel", "Core i7-10700K", 5100, 8, 0, 16, 125, True, 0.93),
    ("Core i9-10850K", "Intel", "Core i9-10900K", 5200, 10, 0, 20, 125, True, 0.85),
    ("Core i9-10900F", "Intel", "Core i9-10900", 5200, 10, 0, 20, 65, False, 0.93),
    ("Core i9-10900KF", "Intel", "Core i9-10900K", 5300, 10, 0, 20, 125, True, 0.95),
    ("Core i7-11700F", "Intel", "Core i7-11700", 4900, 8, 0, 16, 65, False, 0.94),
    ("Core i9-11900F", "Intel", "Core i9-11900", 5200, 8, 0, 16, 65, False, 0.94),
    # AMD AM4 extras
    ("Ryzen 3 4100", "AMD", "Ryzen 3 3100", 4000, 4, 0, 8, 65, True, 0.95),
    ("Ryzen 5 4500", "AMD", "Ryzen 5 3600", 4100, 6, 0, 12, 65, True, 0.65),
    ("Ryzen 5 3600XT", "AMD", "Ryzen 5 3600X", 4500, 6, 0, 12, 95, True, 1.0),
    ("Ryzen 7 3800XT", "AMD", "Ryzen 7 3800X", 4700, 8, 0, 16, 105, True, 1.0),
    ("Ryzen 5 5600GT", "AMD", "Ryzen 5 5600X", 4600, 6, 0, 12, 65, True, 0.67),
    ("Ryzen 5 5500X3D", "AMD", "Ryzen 5 5600X3D", 4000, 6, 0, 12, 105, False, 0.87),
    ("Ryzen 7 5700", "AMD", "Ryzen 7 5800X", 4600, 8, 0, 16, 65, True, 0.55),
]

MOTHERBOARDS += [
    ("ASUS", "ROG Strix Z590-E Gaming WiFi", "LGA 1200", "Z590", ATX, "DDR4", 380),
    ("ASUS", "TUF Gaming Z590-Plus WiFi", "LGA 1200", "Z590", ATX, "DDR4", 230),
    ("ASUS", "ROG Strix B560-F Gaming WiFi", "LGA 1200", "B560", ATX, "DDR4", 200),
    ("ASUS", "Prime B560-Plus", "LGA 1200", "B560", ATX, "DDR4", 130),
    ("ASUS", "Prime H510M-E", "LGA 1200", "H510", MATX, "DDR4", 80),
    ("MSI", "MAG Z590 Tomahawk WiFi", "LGA 1200", "Z590", ATX, "DDR4", 250),
    ("MSI", "MAG B560 Tomahawk WiFi", "LGA 1200", "B560", ATX, "DDR4", 180),
    ("MSI", "PRO B560M-A", "LGA 1200", "B560", MATX, "DDR4", 110),
    ("GIGABYTE", "Z590 AORUS Elite AX", "LGA 1200", "Z590", ATX, "DDR4", 240),
    ("GIGABYTE", "B560M DS3H", "LGA 1200", "B560", MATX, "DDR4", 100),
    ("ASRock", "Z590 Steel Legend WiFi 6E", "LGA 1200", "Z590", ATX, "DDR4", 230),
    ("ASRock", "B560M Pro4", "LGA 1200", "B560", MATX, "DDR4", 110),
    ("ASRock", "H510M-HDV", "LGA 1200", "H510", MATX, "DDR4", 70),
    ("ASUS", "ROG Strix Z390-E Gaming", "LGA 1151 (Coffee Lake)", "Z390", ATX, "DDR4", 250),
    ("ASUS", "TUF Z390-Plus Gaming", "LGA 1151 (Coffee Lake)", "Z390", ATX, "DDR4", 150),
    ("ASUS", "Prime B365M-A", "LGA 1151 (Coffee Lake)", "B365", MATX, "DDR4", 90),
    ("GIGABYTE", "Z390 AORUS Pro", "LGA 1151 (Coffee Lake)", "Z390", ATX, "DDR4", 190),
    ("GIGABYTE", "B365M DS3H", "LGA 1151 (Coffee Lake)", "B365", MATX, "DDR4", 75),
    ("ASRock", "Z390 Phantom Gaming 4", "LGA 1151 (Coffee Lake)", "Z390", ATX, "DDR4", 120),
]
LOCKED_CHIPSETS |= {"B560", "H510", "B365"}

PSUS += [
    ("CORSAIR", "RM650", 650, "ATX", "Modular", 90), ("CORSAIR", "CX750M", 750, "ATX", "Modular", 85),
    ("Seasonic", "Focus GX-650", 650, "ATX", "Modular", 110), ("be quiet!", "System Power 10 550W", 550, "ATX", "None", 60),
    ("EVGA", "600 W1", 600, "ATX", "None", 50), ("Thermaltake", "Smart 500W", 500, "ATX", "None", 40),
    ("MSI", "MAG A650BN", 650, "ATX", "None", 60), ("Cooler Master", "MWE Bronze 650 V2", 650, "ATX", "None", 60),
]

CASES += [
    ("NZXT", "H510 Flow", ATX, "Mid Tower", 90), ("NZXT", "H210", ITX, "Micro", 90),
    ("Fractal Design", "Focus 2", ATX, "Mid Tower", 70), ("Fractal Design", "Define 7 Compact", ATX, "Mid Tower", 110),
    ("Fractal Design", "Ridge", ITX, "Micro", 130), ("CORSAIR", "4000X RGB", ATX, "Mid Tower", 130),
    ("Lian Li", "LANCOOL 205 Mesh", ATX, "Mid Tower", 70), ("Lian Li", "O11 Air Mini", ATX, "Mid Tower", 110),
    ("Phanteks", "P400A", ATX, "Mid Tower", 80), ("Cooler Master", "MasterBox Q500L", ATX, "Mid Tower", 60),
    ("be quiet!", "Pure Base 501 Airflow", ATX, "Mid Tower", 100), ("Montech", "X3 Mesh", ATX, "Mid Tower", 60),
]


# ================================================================ Batch 3: new categories
# Workstation GPUs: manufacturer, name, stock chipset to base on, performance factor, VRAM, watts, price factor
PRO_GPUS = [
    # Founders Edition with no stock part; mod/CustomModels gives it the FE look.
    ("NVIDIA", "GeForce RTX 5090 Founders Edition", "GeForce RTX 5090", 1.0, 32, 575, 0.95),
    ("NVIDIA", "RTX PRO 6000 Blackwell Workstation Edition", "GeForce RTX 5090", 1.08, 96, 600, 4.25),
    ("NVIDIA", "RTX PRO 5000 Blackwell", "GeForce RTX 5080", 1.05, 48, 300, 4.5),
    ("NVIDIA", "RTX PRO 4500 Blackwell", "GeForce RTX 5070 Ti", 1.0, 32, 200, 3.5),
    ("NVIDIA", "RTX PRO 4000 Blackwell", "GeForce RTX 5070", 1.0, 24, 140, 2.7),
    ("NVIDIA", "RTX 6000 Ada Generation", "GeForce RTX 4090", 0.92, 48, 300, 4.25),
    ("NVIDIA", "RTX 5000 Ada Generation", "GeForce RTX 4080", 0.9, 32, 250, 3.3),
    ("NVIDIA", "RTX 4500 Ada Generation", "GeForce RTX 4070 Ti SUPER", 0.85, 24, 210, 2.8),
    ("NVIDIA", "RTX 4000 Ada Generation", "GeForce RTX 4060 Ti", 1.0, 20, 130, 3.1),
    ("NVIDIA", "RTX 4000 SFF Ada Generation", "GeForce RTX 4060 Ti", 0.85, 20, 70, 3.1),
    ("NVIDIA", "RTX A6000", "GeForce RTX 3090", 0.95, 48, 300, 3.1),
    ("NVIDIA", "RTX A5000", "GeForce RTX 3080", 0.9, 24, 230, 3.2),
    ("NVIDIA", "RTX A4000", "GeForce RTX 3060 Ti", 1.0, 16, 140, 2.5),
    ("AMD", "Radeon PRO W7900", "Radeon RX 7900 XTX", 0.9, 48, 295, 4.0),
    ("AMD", "Radeon PRO W7800", "Radeon RX 7900 XT", 0.88, 32, 260, 2.8),
    ("AMD", "Radeon PRO W7700", "Radeon RX 7800 XT", 0.85, 16, 190, 2.0),
    ("AMD", "Radeon AI PRO R9700", "Radeon RX 9070 XT", 1.0, 32, 300, 2.2),
    ("Intel", "Arc Pro B60", "Intel Arc B580", 1.0, 24, 200, 2.0),
]

# Liquid-cooled GPUs: manufacturer, name, air chipset for benchmarks, VRAM, price factor vs air reference
WATER_GPUS = [
    ("MSI", "GeForce RTX 5090 Suprim Liquid SOC", "GeForce RTX 5090", 32, 1.25),
    ("MSI", "GeForce RTX 5080 Suprim Liquid SOC", "GeForce RTX 5080", 16, 1.25),
    ("MSI", "GeForce RTX 4090 Suprim Liquid X", "GeForce RTX 4090", 24, 1.2),
    ("MSI", "GeForce RTX 4080 Suprim Liquid X", "GeForce RTX 4080", 16, 1.2),
    ("MSI", "GeForce RTX 3080 Sea Hawk X", "GeForce RTX 3080", 10, 1.15),
    ("GIGABYTE", "AORUS GeForce RTX 5090 Xtreme Waterforce", "GeForce RTX 5090", 32, 1.3),
    ("GIGABYTE", "AORUS GeForce RTX 4090 Xtreme Waterforce", "GeForce RTX 4090", 24, 1.25),
    ("GIGABYTE", "AORUS GeForce RTX 4090 Xtreme Waterforce WB", "GeForce RTX 4090", 24, 1.25),
    ("GIGABYTE", "AORUS GeForce RTX 4080 Xtreme Waterforce", "GeForce RTX 4080", 16, 1.2),
    ("ASUS", "ROG Astral LC GeForce RTX 5090 OC", "GeForce RTX 5090", 32, 1.35),
    ("ASUS", "ROG Strix LC GeForce RTX 4090 OC", "GeForce RTX 4090", 24, 1.3),
    ("ASUS", "ROG Strix LC Radeon RX 6900 XT OC", "Radeon RX 6900 XT", 16, 1.2),
    ("ASUS", "ROG Strix LC Radeon RX 6800 XT OC", "Radeon RX 6800 XT", 16, 1.2),
    ("INNO3D", "GeForce RTX 5090 iChill Frostbite", "GeForce RTX 5090", 32, 1.3),
    ("INNO3D", "GeForce RTX 4090 iChill Frostbite", "GeForce RTX 4090", 24, 1.25),
    ("PowerColor", "Liquid Devil Radeon RX 7900 XTX", "Radeon RX 7900 XTX", 24, 1.3),
    ("PowerColor", "Liquid Devil Radeon RX 6950 XT", "Radeon RX 6950 XT", 16, 1.25),
    ("PowerColor", "Liquid Devil Ultimate Radeon RX 6900 XT", "Radeon RX 6900 XT", 16, 1.3),
    ("ASRock", "Radeon RX 7900 XTX Aqua OC", "Radeon RX 7900 XTX", 24, 1.35),
    ("Sapphire", "TOXIC Radeon RX 6900 XT Limited Edition", "Radeon RX 6900 XT", 16, 1.3),
    ("EVGA", "GeForce RTX 3090 Ti FTW3 Ultra Hybrid", "GeForce RTX 3090 Ti", 24, 1.15),
    ("EVGA", "GeForce RTX 3080 Ti FTW3 Ultra Hybrid", "GeForce RTX 3080 Ti", 12, 1.15),
    ("EVGA", "GeForce RTX 3090 K|NGP|N Hybrid", "GeForce RTX 3090", 24, 1.4),
]

# Xeon W on LGA 2066 (real parts need C422 boards, added below)
CPUS += [
    ("Xeon W-2295", "Intel", "Core i9-10980XE Extreme Edition", 4600, 18, 0, 36, 165, False, 1.36),
    ("Xeon W-2275", "Intel", "Core i9-10980XE Extreme Edition", 4600, 14, 0, 28, 165, False, 1.22),
    ("Xeon W-2265", "Intel", "Core i9-10980XE Extreme Edition", 4600, 12, 0, 24, 165, False, 0.96),
    ("Xeon W-2255", "Intel", "Core i9-10980XE Extreme Edition", 4500, 10, 0, 20, 165, False, 0.79),
    ("Xeon W-2245", "Intel", "Core i9-10980XE Extreme Edition", 4700, 8, 0, 16, 155, False, 0.68),
    ("Xeon W-2235", "Intel", "Core i9-10980XE Extreme Edition", 4600, 6, 0, 12, 130, False, 0.57),
    ("Xeon W-2195", "Intel", "Core i9-7980XE", 4300, 18, 0, 36, 140, False, 1.28),
    ("Xeon W-2175", "Intel", "Core i9-7980XE", 4300, 14, 0, 28, 140, False, 0.97),
    ("Xeon W-2155", "Intel", "Core i9-7900X", 4500, 10, 0, 20, 140, False, 1.44),
    ("Xeon W-2145", "Intel", "Core i7-7820X", 4500, 8, 0, 16, 140, False, 1.86),
    ("Xeon W-2135", "Intel", "Core i7-7800X", 4500, 6, 0, 12, 140, False, 1.59),
    ("Xeon W-2125", "Intel", "Core i7-7740X", 4500, 4, 0, 8, 120, False, 1.31),
]
MOTHERBOARDS += [
    ("ASUS", "WS C422 PRO/SE", "LGA 2066", "C422", ATX, "DDR4", 400),
    ("ASUS", "WS C422 SAGE/10G", "LGA 2066", "C422", EATX, "DDR4", 650),
    ("Supermicro", "X11SRA", "LGA 2066", "C422", ATX, "DDR4", 450),
    ("GIGABYTE", "MW51-HP0", "LGA 2066", "C422", EATX, "DDR4", 500),
]
LOCKED_CHIPSETS |= {"C422"}

# Peripherals: table -> list of (manufacturer, name, price, extra fields)
W, NW = {"Wireless": "Yes"}, {"Wireless": "No"}
UW, STD = {"Widescreen": "Yes"}, {"Widescreen": "No"}
XL, NORMAL = {"Size": "Extended"}, {"Size": "Normal"}
PERIPHERALS = {
    "Monitors": [
        ("ASUS", "ROG Swift PG27AQDM", 900, STD), ("ASUS", "ROG Swift OLED PG32UCDM", 1300, STD),
        ("ASUS", "ROG Strix XG27ACS", 300, STD), ("ASUS", "TUF Gaming VG27AQ3A", 200, STD),
        ("ASUS", "ROG Swift OLED PG34WCDM", 1100, UW),
        ("LG", "UltraGear 27GR95QE", 800, STD), ("LG", "UltraGear 27GS95QE", 900, STD),
        ("LG", "UltraGear 32GS95UE", 1400, STD), ("LG", "UltraGear 27GP850-B", 400, STD),
        ("LG", "UltraGear 45GR95QE", 1700, UW), ("LG", "UltraGear 34GP83A-B", 500, UW),
        ("Samsung", "Odyssey G7 32\"", 700, STD), ("Samsung", "Odyssey OLED G8 32\"", 1300, STD),
        ("Samsung", "Odyssey G5 27\"", 300, STD), ("Samsung", "Odyssey OLED G9 49\"", 1600, UW),
        ("Samsung", "Odyssey Neo G9 57\"", 2500, UW),
        ("Dell", "Alienware AW2725DF", 900, STD), ("Dell", "Alienware AW3225QF", 1200, STD),
        ("Dell", "Alienware AW3423DWF", 900, UW), ("Dell", "S2721DGF", 400, STD),
        ("MSI", "MAG 271QPX QD-OLED", 700, STD), ("MSI", "MPG 321URX QD-OLED", 1000, STD),
        ("MSI", "MAG 274QRF-QD", 330, STD),
        ("GIGABYTE", "M27Q", 300, STD), ("GIGABYTE", "AORUS FO32U2P", 1300, STD),
        ("BenQ", "ZOWIE XL2546K", 600, STD), ("BenQ", "MOBIUZ EX2710Q", 400, STD),
        ("AOC", "24G2SP", 180, STD), ("AOC", "Q27G3XMN", 330, STD),
        ("Acer", "Nitro XV272U", 300, STD), ("Acer", "Predator X27U", 1000, STD),
        ("Philips", "Evnia 27M2N5500", 300, STD), ("CORSAIR", "XENEON 27QHD240", 900, STD),
    ],
    "Keyboards": [
        ("Logitech", "G PRO X TKL LIGHTSPEED", 200, W), ("Logitech", "G915 X LIGHTSPEED", 230, W),
        ("Logitech", "G213 Prodigy", 60, NW),
        ("Razer", "BlackWidow V4 Pro", 230, NW), ("Razer", "Huntsman V3 Pro", 250, NW),
        ("Razer", "Huntsman Mini", 120, NW), ("Razer", "DeathStalker V2 Pro", 250, W),
        ("CORSAIR", "K70 RGB PRO", 170, NW), ("CORSAIR", "K100 RGB", 230, NW), ("CORSAIR", "K65 PLUS Wireless", 160, W),
        ("SteelSeries", "Apex Pro TKL (2023)", 190, NW), ("SteelSeries", "Apex 3", 70, NW), ("SteelSeries", "Apex 7", 160, NW),
        ("HyperX", "Alloy Origins Core", 90, NW), ("HyperX", "Alloy Origins 65", 100, NW),
        ("Wooting", "60HE", 175, NW), ("Wooting", "Two HE", 200, NW),
        ("Keychron", "Q1 Pro", 200, W), ("Keychron", "K2 V2", 80, W),
        ("ASUS", "ROG Azoth", 250, W), ("ASUS", "ROG Strix Scope II 96 Wireless", 180, W),
        ("Ducky", "One 3", 120, NW), ("MSI", "Vigor GK71 Sonic", 100, NW),
        ("Glorious", "GMMK Pro", 170, NW), ("Cooler Master", "CK721", 120, W),
    ],
    "Mice": [
        ("Logitech", "G PRO X SUPERLIGHT 2", 160, W), ("Logitech", "G502 X PLUS", 160, W),
        ("Logitech", "G305 LIGHTSPEED", 50, W), ("Logitech", "G502 HERO", 80, NW), ("Logitech", "G703 LIGHTSPEED", 100, W),
        ("Razer", "DeathAdder V3 Pro", 150, W), ("Razer", "Viper V3 Pro", 160, W), ("Razer", "Basilisk V3", 70, NW),
        ("Razer", "DeathAdder Essential", 30, NW), ("Razer", "Viper Mini", 40, NW),
        ("ZOWIE", "EC2-C", 70, NW), ("ZOWIE", "EC2-CW", 150, W),
        ("SteelSeries", "Aerox 5 Wireless", 140, W), ("SteelSeries", "Rival 3", 30, NW), ("SteelSeries", "Prime Wireless", 130, W),
        ("CORSAIR", "M75 Wireless", 130, W), ("CORSAIR", "Dark Core RGB PRO", 90, W), ("CORSAIR", "Harpoon RGB Wireless", 50, W),
        ("Glorious", "Model O 2 Wireless", 100, W), ("Glorious", "Model D 2", 60, NW),
        ("Pulsar", "X2V2", 90, W), ("Lamzu", "Atlantis Mini", 100, W), ("HyperX", "Pulsefire Haste 2", 60, NW),
        ("Finalmouse", "UltralightX", 190, W), ("Endgame Gear", "OP1 8k", 70, NW),
    ],
    "Headsets": [
        ("SteelSeries", "Arctis Nova Pro Wireless", 350, {}), ("SteelSeries", "Arctis Nova 7", 180, {}),
        ("SteelSeries", "Arctis Nova 1", 60, {}),
        ("HyperX", "Cloud III", 100, {}), ("HyperX", "Cloud Alpha Wireless", 200, {}), ("HyperX", "Cloud II", 80, {}),
        ("Logitech", "G PRO X 2 LIGHTSPEED", 250, {}), ("Logitech", "G733 LIGHTSPEED", 130, {}), ("Logitech", "G435", 80, {}),
        ("Razer", "BlackShark V2 Pro", 200, {}), ("Razer", "Kraken V4", 200, {}), ("Razer", "BlackShark V2 X", 60, {}),
        ("CORSAIR", "VIRTUOSO RGB WIRELESS XT", 270, {}), ("CORSAIR", "HS80 RGB WIRELESS", 150, {}),
        ("CORSAIR", "HS65 SURROUND", 80, {}),
        ("Sennheiser", "HD 560S", 230, {}), ("Audeze", "Maxwell", 300, {}), ("Astro", "A50 X", 380, {}),
        ("beyerdynamic", "MMX 300 (2nd Gen)", 270, {}), ("Turtle Beach", "Stealth Pro", 330, {}),
        ("ASUS", "ROG Delta II", 230, {}),
    ],
    "Mousepads": [
        ("SteelSeries", "QcK Heavy XXL", 50, XL), ("SteelSeries", "QcK Large", 20, NORMAL),
        ("Razer", "Gigantus V2 XXL", 30, XL), ("Razer", "Strider Large", 40, NORMAL), ("Razer", "Goliathus Chroma Extended", 60, XL),
        ("Logitech", "G640", 30, NORMAL), ("Logitech", "G840 XL", 50, XL),
        ("CORSAIR", "MM300 PRO Extended", 40, XL), ("CORSAIR", "MM700 RGB Extended", 80, XL),
        ("Artisan", "Hien FX Soft L", 60, NORMAL), ("Glorious", "XXL Extended", 30, XL),
        ("HyperX", "Pulsefire Mat XL", 35, XL), ("ZOWIE", "G-SR", 50, NORMAL),
        ("ASUS", "ROG Sheath", 40, XL), ("Lethal Gaming Gear", "Saturn Pro", 60, NORMAL),
    ],
    "Microphones": [
        ("Shure", "SM7B", 400, {}), ("Shure", "MV7+", 280, {}), ("Elgato", "Wave:3", 150, {}),
        ("Blue", "Yeti", 130, {}), ("Blue", "Yeti X", 170, {}), ("RODE", "PodMic USB", 200, {}),
        ("RODE", "NT-USB+", 170, {}), ("HyperX", "QuadCast 2 S", 160, {}), ("HyperX", "SoloCast", 60, {}),
        ("Razer", "Seiren V3 Chroma", 130, {}), ("AKG", "Lyra", 150, {}), ("Audio-Technica", "AT2020USB-X", 150, {}),
        ("FIFINE", "AmpliGame A8", 50, {}), ("NZXT", "Capsule Mini", 50, {}),
    ],
}


# ================================================================ Batch 4: 2026 launches + older backfill (researched 2026-10-30)
CHIPSET_FALLBACK.update({
    "Radeon RX 9070 GRE": ("Radeon RX 9070", 0.85),   # global launch at Computex 2026, 48 CU / 12GB
    "Intel Arc B770": ("Intel Arc B580", 1.35),        # BMG-G31, 16GB; launch details from a single secondary source
})
VRAM_VARIANTS.update({"Radeon RX 9070 GRE": [12], "Intel Arc B770": [16]})
DISPLAY.update({"Intel Arc B770": "Arc B770", "Geforce RTX 2060": "GeForce RTX 2060", "Geforce RTX 2070": "GeForce RTX 2070",
                "GeForce RTX 2060 Super": "GeForce RTX 2060 SUPER", "GeForce RTX 2070 Super": "GeForce RTX 2070 SUPER",
                "GeForce RTX 2080 Super": "GeForce RTX 2080 SUPER", "Radeon RX560": "Radeon RX 560",
                "Radeon RX570": "Radeon RX 570", "Radeon RX580": "Radeon RX 580", "Radeon RX590": "Radeon RX 590",
                "Radeon RX5700": "Radeon RX 5700", "Radeon RX5700 XT": "Radeon RX 5700 XT"})

NV20 = ["Geforce RTX 2060", "GeForce RTX 2060 Super", "Geforce RTX 2070", "GeForce RTX 2070 Super", "GeForce RTX 2080",
        "GeForce RTX 2080 Super", "GeForce RTX 2080 Ti"]
GTX10 = ["GeForce GTX 1050", "GeForce GTX 1050 Ti", "GeForce GTX 1060", "GeForce GTX 1070", "GeForce GTX 1070 Ti",
         "GeForce GTX 1080", "GeForce GTX 1080 Ti"]
POLARIS = ["Radeon RX560", "Radeon RX570", "Radeon RX580", "Radeon RX590"]
NAVI1 = ["Radeon RX 5500 XT", "Radeon RX 5600 XT", "Radeon RX5700", "Radeon RX5700 XT"]

GPU_LINES += [
    # 2026
    ("Sapphire", "PULSE {c}", 0, ["Radeon RX 9070 GRE"]),
    ("PowerColor", "Hellhound {c}", 1, ["Radeon RX 9070 GRE"]),
    ("PowerColor", "Reaper {c}", 0, ["Radeon RX 9070 GRE"]),
    ("XFX", "Speedster SWFT {c}", 0, ["Radeon RX 9070 GRE"]),
    ("ASRock", "{c} Challenger OC", 0, ["Radeon RX 9070 GRE", "Intel Arc B770"]),
    ("GIGABYTE", "{c} Gaming OC", 1, ["Radeon RX 9070 GRE"]),
    ("Intel", "{c} Limited Edition", 0, ["Intel Arc B770"]),
    ("Sparkle", "Intel {c} Titan OC", 1, ["Intel Arc B770"]),
    # RTX 20 / GTX 10 / Polaris / Navi 1x partner cards
    ("ASUS", "ROG Strix {c} OC", 2, NV20 + span(GTX10, "GeForce GTX 1060", "GeForce GTX 1080 Ti") + span(POLARIS, "Radeon RX570", "Radeon RX590") + NAVI1),
    ("ASUS", "Dual {c} OC", 0, span(NV20, "Geforce RTX 2060", "GeForce RTX 2070 Super") + span(GTX10, "GeForce GTX 1050", "GeForce GTX 1070") + ["Radeon RX580"]),
    ("ASUS", "TUF Gaming {c} OC", 1, ["Geforce RTX 2060", "Geforce RTX 2070", "Radeon RX 5600 XT", "Radeon RX5700 XT"]),
    ("MSI", "{c} Gaming X Trio", 2, span(NV20, "Geforce RTX 2070", "GeForce RTX 2080 Ti")),
    ("MSI", "{c} Gaming X", 1, span(NV20, "Geforce RTX 2060", "GeForce RTX 2070 Super") + GTX10 + POLARIS + NAVI1),
    ("MSI", "{c} Ventus OC", 0, NV20),
    ("MSI", "{c} Armor OC", 0, span(GTX10, "GeForce GTX 1050", "GeForce GTX 1080") + span(POLARIS, "Radeon RX570", "Radeon RX580")),
    ("EVGA", "{c} XC Ultra Gaming", 1, NV20 + span(GTX10, "GeForce GTX 1060", "GeForce GTX 1080 Ti")),
    ("EVGA", "{c} FTW3 Ultra Gaming", 2, span(NV20, "GeForce RTX 2070 Super", "GeForce RTX 2080 Ti")),
    ("EVGA", "{c} FTW3 Gaming", 2, span(GTX10, "GeForce GTX 1070", "GeForce GTX 1080 Ti")),
    ("GIGABYTE", "{c} Windforce OC", 0, NV20 + span(GTX10, "GeForce GTX 1050", "GeForce GTX 1080")),
    ("GIGABYTE", "{c} Gaming OC", 1, NV20 + span(GTX10, "GeForce GTX 1060", "GeForce GTX 1080 Ti") + span(POLARIS, "Radeon RX570", "Radeon RX590") + NAVI1),
    ("GIGABYTE", "AORUS {c} Xtreme", 2, span(NV20, "Geforce RTX 2070", "GeForce RTX 2080 Ti") + span(GTX10, "GeForce GTX 1070", "GeForce GTX 1080 Ti")),
    ("ZOTAC", "Gaming {c} AMP", 1, NV20),
    ("ZOTAC", "{c} Mini", 0, span(GTX10, "GeForce GTX 1050", "GeForce GTX 1080 Ti")),
    ("Sapphire", "PULSE {c}", 0, POLARIS + NAVI1),
    ("Sapphire", "NITRO+ {c}", 2, span(POLARIS, "Radeon RX570", "Radeon RX590") + NAVI1),
    ("XFX", "{c} GTS XXX Edition", 0, span(POLARIS, "Radeon RX570", "Radeon RX590")),
    ("XFX", "{c} THICC III Ultra", 1, ["Radeon RX 5600 XT", "Radeon RX5700", "Radeon RX5700 XT"]),
    ("PowerColor", "Red Devil {c}", 2, span(POLARIS, "Radeon RX570", "Radeon RX590") + ["Radeon RX5700", "Radeon RX5700 XT"]),
    ("PowerColor", "Red Dragon {c}", 1, span(POLARIS, "Radeon RX570", "Radeon RX590") + ["Radeon RX5700", "Radeon RX5700 XT"]),
]

CPUS += [
    # 2026 launches
    ("Ryzen 9 9950X3D2", "AMD", "Ryzen 9 9950X3D", 5600, 16, 0, 32, 200, True, 1.29),  # Apr 22 2026, $899, 192MB L3
    ("Ryzen 7 9850X3D", "AMD", "Ryzen 7 9800X3D", 5600, 8, 0, 16, 120, True, 1.04),     # Jan 29 2026, $499
    ("Core Ultra 7 270KF Plus", "Intel", "Core Ultra 7 270K Plus", 5500, 24, 16, 24, 125, True, 0.95),
    ("Core Ultra 5 250KF Plus", "Intel", "Core Ultra 5 250K Plus", 5300, 18, 12, 18, 125, True, 0.95),
    # Older backfill
    ("Core i3-9100", "Intel", "Core i3-8100", 4200, 4, 0, 4, 65, False, 0.85),
    ("Core i5-8500", "Intel", "Core i5-8400", 4100, 6, 0, 6, 65, False, 1.06),
    ("Core i5-9400", "Intel", "Core i5-8400", 4100, 6, 0, 6, 65, False, 1.0),
    ("Core i5-9500", "Intel", "Core i5-8400", 4400, 6, 0, 6, 65, False, 1.0),
    ("Core i7-9700", "Intel", "Core i7-9700K", 4700, 8, 0, 8, 65, False, 0.9),
    ("Core i9-9900", "Intel", "Core i9-9900K", 5000, 8, 0, 16, 65, False, 0.9),
    ("Ryzen 3 2200G", "AMD", "Ryzen 3 1200", 3700, 4, 0, 4, 65, True, 1.0),
    ("Ryzen 5 2400G", "AMD", "Ryzen 5 1500X", 3900, 4, 0, 8, 65, True, 1.0),
    ("Ryzen 3 3200G", "AMD", "Ryzen 3 1300X", 4000, 4, 0, 4, 65, True, 0.8),
    ("Ryzen 5 3400G", "AMD", "Ryzen 5 1500X", 4200, 4, 0, 8, 65, True, 1.0),
    ("Ryzen 5 1600 AF", "AMD", "Ryzen 5 2600", 3600, 6, 0, 12, 65, True, 0.5),
    ("Ryzen 5 3500X", "AMD", "Ryzen 5 3600", 4100, 6, 0, 6, 65, True, 0.7),
]

MOTHERBOARDS += [
    ("GIGABYTE", "B840M FORCE WIFI6E", "AM5", "B840", MATX, "DDR5", 120),
]
LOCKED_CHIPSETS |= {"B840"}


# ================================================================ Batch 5: RAM, high-performance fans, AIOs
# The game has no ECC column, so ECC modules differ from regular sticks only in name.
RAM += [
    # High capacity DDR5
    ("CORSAIR", "Vengeance DDR5", "DDR5", 5600, 40, 1.25, [48, 64], "N/A", 1.0),
    ("CORSAIR", "Vengeance RGB DDR5", "DDR5", 6000, 30, 1.40, [48], "RGB", 1.15),
    ("G.SKILL", "Trident Z5 RGB", "DDR5", 6400, 32, 1.40, [48], "RGB", 1.2),
    ("G.SKILL", "Flare X5", "DDR5", 6000, 30, 1.35, [48], "N/A", 1.05),
    ("G.SKILL", "Ripjaws M5 RGB", "DDR5", 5600, 46, 1.25, [64], "RGB", 1.05),
    ("Kingston", "FURY Beast DDR5", "DDR5", 5600, 40, 1.25, [48, 64], "N/A", 0.95),
    ("Crucial", "Pro DDR5", "DDR5", 5600, 46, 1.10, [48, 64], "N/A", 0.9),
    ("Team Group", "T-Create Expert DDR5", "DDR5", 6000, 34, 1.35, [48], "N/A", 1.0),
    # High capacity DDR4
    ("CORSAIR", "Vengeance LPX DDR4", "DDR4", 3200, 22, 1.35, [64], "N/A", 1.0),
    ("Kingston", "FURY Beast DDR4", "DDR4", 3200, 18, 1.35, [64], "N/A", 1.0),
    # ECC unbuffered (works on AM5/AM4 consumer boards)
    ("Kingston", "Server Premier DDR5 ECC", "DDR5", 5600, 46, 1.10, [16, 32, 48], "N/A", 1.15),
    ("Kingston", "Server Premier DDR5 ECC", "DDR5", 4800, 40, 1.10, [16, 32], "N/A", 1.1),
    ("Crucial", "DDR5 ECC UDIMM", "DDR5", 5600, 46, 1.10, [16, 32, 48], "N/A", 1.12),
    ("Kingston", "Server Premier DDR4 ECC", "DDR4", 3200, 22, 1.20, [16, 32], "N/A", 1.15),
    ("Crucial", "DDR4 ECC UDIMM", "DDR4", 3200, 22, 1.20, [16, 32], "N/A", 1.12),
    # Fast DDR5
    ("G.SKILL", "Trident Z5 RGB", "DDR5", 8000, 38, 1.45, [24], "RGB", 1.5),
    ("G.SKILL", "Trident Z5 CK", "DDR5", 8200, 40, 1.40, [24], "RGB", 1.6),
    ("G.SKILL", "Trident Z5 Royal Neo", "DDR5", 8000, 38, 1.45, [24], "RGB", 1.8),
    ("CORSAIR", "Vengeance RGB DDR5", "DDR5", 8000, 38, 1.45, [24], "RGB", 1.5),
    ("CORSAIR", "Dominator Titanium RGB DDR5", "DDR5", 8000, 38, 1.45, [24, 48], "RGB", 1.7),
    ("Kingston", "FURY Renegade DDR5 RGB CUDIMM", "DDR5", 8400, 40, 1.45, [24], "RGB", 1.7),
    ("Kingston", "FURY Renegade DDR5 RGB", "DDR5", 7600, 38, 1.45, [16, 24], "RGB", 1.4),
    ("Team Group", "T-Force Xtreem DDR5", "DDR5", 8200, 38, 1.45, [24], "N/A", 1.5),
    ("ADATA", "XPG Lancer RGB DDR5", "DDR5", 7200, 34, 1.40, [16], "RGB", 1.3),
    ("Patriot", "Viper Xtreme 5 RGB DDR5", "DDR5", 8200, 38, 1.45, [24], "RGB", 1.6),
    ("Crucial", "Pro OC DDR5", "DDR5", 6400, 32, 1.35, [16, 32], "N/A", 1.1),
    # Fast DDR4
    ("G.SKILL", "Trident Z Royal DDR4", "DDR4", 4000, 15, 1.50, [8, 16], "RGB", 1.6),
    ("G.SKILL", "Ripjaws V DDR4", "DDR4", 4400, 19, 1.50, [8, 16], "N/A", 1.4),
    ("Team Group", "T-Force Xtreem ARGB DDR4", "DDR4", 4000, 18, 1.45, [8, 16], "RGB", 1.4),
]

# High airflow / static pressure fans (manufacturer specs; CFM, mmH2O)
FANS += [
    ("Noctua", "NF-F12 industrialPPC-3000 PWM", 120, 109.9, 7.63, 30, "N/A"),
    ("Noctua", "NF-F12 industrialPPC-2000 PWM", 120, 71.6, 3.94, 25, "N/A"),
    ("Noctua", "NF-A14 industrialPPC-3000 PWM", 140, 158.5, 10.52, 32, "N/A"),
    ("Noctua", "NF-A14 industrialPPC-2000 PWM", 140, 107.5, 4.18, 27, "N/A"),
    ("Noctua", "NF-A12x25 G2 PWM", 120, 66.2, 3.06, 40, "N/A"),
    ("ARCTIC", "P12 Max", 120, 81.0, 4.3, 12, "N/A"), ("ARCTIC", "P14 Max", 140, 102.0, 4.6, 15, "N/A"),
    ("be quiet!", "Silent Wings Pro 4 120mm", 120, 72.2, 5.86, 33, "N/A"),
    ("be quiet!", "Silent Wings Pro 4 140mm", 140, 89.3, 4.38, 35, "N/A"),
    ("CORSAIR", "ML120 PRO", 120, 75.0, 4.2, 30, "N/A"), ("CORSAIR", "ML140 PRO", 140, 97.0, 3.0, 35, "N/A"),
    ("CORSAIR", "iCUE LINK LX120 RGB", 120, 63.1, 2.84, 30, "RGB"),
    ("Lian Li", "UNI FAN P28 120", 120, 82.0, 6.3, 30, "ARGB"),
    ("Lian Li", "UNI FAN TL LCD 120", 120, 69.0, 3.0, 45, "ARGB"),
    ("Phanteks", "T30-120 (3000 RPM)", 120, 70.0, 4.65, 33, "N/A"),
    ("Thermalright", "TL-B12 Extreme", 120, 108.0, 8.2, 18, "N/A"),
    ("EKWB", "EK-Vardar EVO 120ER", 120, 77.0, 3.16, 25, "N/A"),
    ("Cooler Master", "SickleFlow 120 V2", 120, 62.0, 2.5, 12, "ARGB"),
    ("Delta", "AFB1212SHE", 120, 151.0, 11.2, 25, "N/A"),
    ("Silverstone", "Air Penetrator AP181", 180, 132.0, 4.1, 40, "N/A"),
]

LIQUID_COOLERS += [
    ("ARCTIC", "Liquid Freezer III Pro 280", 140, 2, 90, "N/A"), ("ARCTIC", "Liquid Freezer III Pro 360", 120, 3, 100, "N/A"),
    ("ARCTIC", "Liquid Freezer III Pro 420", 140, 3, 120, "N/A"), ("ARCTIC", "Liquid Freezer III Pro 360 A-RGB", 120, 3, 110, "ARGB"),
    ("CORSAIR", "iCUE LINK TITAN 360 RX RGB", 120, 3, 210, "RGB"), ("CORSAIR", "iCUE LINK TITAN 240 RX RGB", 120, 2, 170, "RGB"),
    ("CORSAIR", "iCUE H170i ELITE LCD XT", 140, 3, 300, "RGB"),
    ("NZXT", "Kraken Plus 360", 120, 3, 200, "RGB"), ("NZXT", "Kraken Elite 280", 140, 2, 260, "RGB"),
    ("NZXT", "Kraken Elite 240 RGB", 120, 2, 230, "RGB"),
    ("Lian Li", "Galahad II LCD 360", 120, 3, 210, "ARGB"), ("Lian Li", "HydroShift II LCD-C 360TL", 120, 3, 230, "ARGB"),
    ("Lian Li", "Galahad II Performance 280", 140, 2, 150, "ARGB"),
    ("Thermalright", "Grand Vision 360", 120, 3, 110, "ARGB"), ("Thermalright", "Wonder Vision 360", 120, 3, 130, "ARGB"),
    ("Thermalright", "Frozen Warframe 360", 120, 3, 90, "ARGB"),
    ("Deepcool", "LQ360", 120, 3, 140, "ARGB"), ("Deepcool", "Mystique 360", 120, 3, 170, "ARGB"),
    ("MSI", "MPG CoreLiquid I360", 120, 3, 200, "ARGB"), ("MSI", "MAG CoreLiquid I240", 120, 2, 120, "ARGB"),
    ("ASUS", "ROG Ryujin III 360 Extreme", 120, 3, 350, "ARGB"), ("ASUS", "ROG Strix LC III 240 ARGB", 120, 2, 170, "ARGB"),
    ("EKWB", "EK-Nucleus AIO CR240 Lux D-RGB", 120, 2, 130, "ARGB"),
    ("Alphacool", "Core Ocean T38 360", 120, 3, 130, "ARGB"), ("Alphacool", "Eisbaer Aurora 420", 140, 3, 180, "ARGB"),
    ("Cooler Master", "MasterLiquid 360 Atmos", 120, 3, 160, "ARGB"), ("Cooler Master", "MasterLiquid PL360 Flux", 120, 3, 170, "ARGB"),
    ("be quiet!", "Silent Loop 3 420", 140, 3, 180, "ARGB"), ("be quiet!", "Pure Loop 2 280", 140, 2, 110, "ARGB"),
    ("be quiet!", "Pure Loop 2 240", 120, 2, 100, "ARGB"),
    ("Fractal Design", "Lumen S36 RGB", 120, 3, 130, "RGB"), ("Phanteks", "Glacier One 360D30", 120, 3, 170, "ARGB"),
    ("Thermaltake", "TH420 V2 Ultra ARGB", 140, 3, 220, "ARGB"),
]


# ================================================================ Batch 6: PSUs (high wattage, ATX 3.x, SFX, budget)
PSUS += [
    # Flagship / high wattage
    ("CORSAIR", "AX1600i", 1600, "ATX", "Modular", 600), ("CORSAIR", "HX1200i", 1200, "ATX", "Modular", 280),
    ("CORSAIR", "RM1000x Shift", 1000, "ATX", "Modular", 210), ("CORSAIR", "RM750x", 750, "ATX", "Modular", 130),
    ("Seasonic", "Prime PX-2200", 2200, "ATX", "Modular", 600), ("Seasonic", "Prime TX-1300", 1300, "ATX", "Modular", 400),
    ("Seasonic", "Vertex PX-1000", 1000, "ATX", "Modular", 250), ("Seasonic", "Focus GX-1200", 1200, "ATX", "Modular", 230),
    ("be quiet!", "Dark Power Pro 13 1300W", 1300, "ATX", "Modular", 400), ("be quiet!", "Dark Power 14 1000W", 1000, "ATX", "Modular", 280),
    ("be quiet!", "Pure Power 13 M 1000W", 1000, "ATX", "Modular", 170), ("be quiet!", "Straight Power 12 1500W", 1500, "ATX", "Modular", 330),
    ("ASUS", "ROG Thor 1600W Titanium III", 1600, "ATX", "Modular", 600), ("ASUS", "ROG Strix 1200W Gold Aura", 1200, "ATX", "Modular", 260),
    ("ASUS", "TUF Gaming 1200G", 1200, "ATX", "Modular", 210),
    ("MSI", "MEG Ai1300P PCIE5", 1300, "ATX", "Modular", 330), ("MSI", "MPG A850G PCIE5", 850, "ATX", "Modular", 140),
    ("MSI", "MAG A850GL PCIE5", 850, "ATX", "Modular", 110),
    ("Thermaltake", "Toughpower GF A3 1200W", 1200, "ATX", "Modular", 200),
    ("NZXT", "C1500 Platinum", 1500, "ATX", "Modular", 330),
    ("Cooler Master", "X Mighty Platinum 2000W", 2000, "ATX", "Modular", 500), ("Cooler Master", "MWE Gold 1250 V2", 1250, "ATX", "Modular", 200),
    ("Super Flower", "Leadex Titanium 1600W", 1600, "ATX", "Modular", 430), ("Super Flower", "Leadex VII Platinum PRO 1300W", 1300, "ATX", "Modular", 280),
    ("EVGA", "SuperNOVA 1600 P+", 1600, "ATX", "Modular", 400), ("EVGA", "SuperNOVA 1300 G+", 1300, "ATX", "Modular", 250),
    ("FSP", "Cannon Pro 2500W", 2500, "ATX", "Modular", 600),
    ("SilverStone", "HELA 2050R Platinum", 2050, "ATX", "Modular", 450),
    ("Lian Li", "EDGE 1300", 1300, "ATX", "Modular", 300), ("Lian Li", "SP850", 850, "SFX", "Modular", 170),
    # SFX
    ("CORSAIR", "SF850", 850, "SFX", "Modular", 190), ("SilverStone", "SX1000 Platinum", 1000, "SFX", "Modular", 260),
    ("be quiet!", "SFX Power 3 450W", 450, "SFX", "None", 75), ("Cooler Master", "V1100 SFX Platinum", 1100, "SFX", "Modular", 270),
    # Budget
    ("CORSAIR", "CX550", 550, "ATX", "None", 60), ("EVGA", "500 W3", 500, "ATX", "None", 45),
    ("Thermaltake", "Smart 600W", 600, "ATX", "None", 50), ("be quiet!", "System Power 11 650W", 650, "ATX", "None", 70),
    ("Seasonic", "G12 GC-750", 750, "ATX", "None", 90), ("MSI", "MAG A750BN PCIE5", 750, "ATX", "None", 75),
]
