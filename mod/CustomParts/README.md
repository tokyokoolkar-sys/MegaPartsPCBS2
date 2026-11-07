# PCBS2 CustomParts

Adds GPU parts that are their own part (own row, own Asset Path key, own slot size) with a custom 3D model.
First part: **GeForce RTX 5090 Founders Edition (Custom Model)**, `GPU_CustomParts_RTX5090FE`, 2 slots, 304 mm.

## How it works

1. **Key.** The part XML's Asset Path is `Prefabs/Custom/GPU_RTX5090FE`, a key the stock catalog doesn't have.
   Once the game's catalog has loaded, the mod adds an Addressables `ResourceLocationMap` that maps the new key to the
   stock RTX 4090 prefab's bundle location. The game then loads the part through its normal Addressables path.
2. **Model.** The game's part behaviour (slots, connectors, scripts) exists only in its own prefabs. So each spawned
   instance (root object named after the part ID) has the stock 4090 meshes hidden and the bundle model added.
   Placement is automatic, with no tuned numbers:
   - **Orientation:** the shroud's long side points to the bracket, and "up" points to the power connector, on both models.
   - **Scale:** game units per mm come from the stock shroud (304 mm). The model's shroud is scaled to its real length.
   - **Position:** the bracket's outer face, the board's bottom edge and the board plane line up with the stock card's.
   - **Collider:** the root collider is refitted to the new model.
   - **Fans and connector:** the fans spin with the stock fans, and the 16-pin connector moves onto the model's power port.
3. **Slots** come from the XML row's `Slot Size` (2). The stock 4090 and other parts that use its prefab are left alone.

## Install (from `out/customparts/`, built by `tools/build_customparts.ps1`)

| Staged file | Goes to (game folder) |
|---|---|
| `Mods/CustomParts.dll` | `Mods\CustomParts.dll` |
| `Mods/CustomParts/parts.txt` | `Mods\CustomParts\parts.txt` |
| `Mods/CustomParts/rtx5090fe` | `Mods\CustomParts\rtx5090fe` |
| `Mods/AirCooledGPU_NVIDIA GeForce RTX 5090 Founders Edition (Custom).xml` | `Mods\` (on Windows, MelonLoader's `Mods` and the XML Part Loader's `mods` are the same folder) |

The staging folder copies the game's own layout, so copying the contents of `out/customparts` onto the game folder installs it.
To uninstall, delete those four files.

## Log lines to look for (MelonLoader console / `MelonLoader\Latest.log`)

```
[GPU_CustomParts_RTX5090FE] model RTX5090FE loaded from rtx5090fe
[GPU_CustomParts_RTX5090FE] catalog registered: Prefabs/Custom/GPU_RTX5090FE -> Prefabs/GPU/NVidia/GPU_NVIDIA_GEFORCE_RTX_4090 ...
[GPU_CustomParts_RTX5090FE] key resolved: Prefabs/Custom/GPU_RTX5090FE -> ...bundle...
[GPU_CustomParts_RTX5090FE] prefab built on GPU_CustomParts_RTX5090FE: ... size 304 x 1xx x ~40 mm ... ~2 slot(s) thick
[GPU_CustomParts_RTX5090FE] moved 16 pin power connector by ... onto power port
```

Also check `PCBS2.XPL.log` to confirm the XML imported.

## Adding a card with the GUI (v2)

Double-click `tools/customparts_gui.cmd`, which runs `uv run --no-project --with tkinterdnd2 tools/customparts_gui.py`.

1. Drop a `.glb` model on the window. It is converted into `unity/ModelBundles/Assets/Models/<Name>/`, and the reference
   parts (shroud, bracket, power connector, PCIe edge, fans) are guessed from the node names. Check the drop-downs.
2. Fill in the name, slot size, shroud length, and optionally VRAM and price. Pick a stats template card, whose
   benchmark numbers are copied.
3. **Build** writes the part XML to `mod/CustomParts/parts/`, adds or replaces the line in `parts.txt` (tuned offset and
   rotation are kept), then runs `tools/build_customparts.ps1`.
4. **Deploy** copies `out/customparts/Mods` into the game. It refuses while the game is running, and it first copies the
   offsets you saved in-game with F9 back into the repo.

## In-game tuner (F8)

The panel tunes the custom part under the mouse, or the last one spawned. Arrows and PgUp/PgDn move it in mm
(length, height, thickness). Shift + the same keys rotate it (about length, height, thickness). `[` `]` change the step,
and F9 saves fields 14 and 15 of `parts.txt` in the game folder.

**Per motherboard (v2.1).** The game puts a card at the same spot relative to its slot in every case, so any leftover
offset comes from the motherboard model. While the card is installed, the panel shows "tuning this build:
<motherboard>": changes and F9 apply to that motherboard only and are saved in `Mods\CustomParts\builds.txt`
(starting from the part default). Motherboards with no entry use the default. Cards refit when installed or moved.
The stock meshes are hidden with `forceRenderingOff`, so the fan control app still lists the GPU fans (its preview
shows the base card's fan model).
