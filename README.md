# MegaParts for PC Building Simulator 2

Mods and tools for PC Building Simulator 2 (MelonLoader, IL2CPP).

## Mods (`mod/`)

| Mod | What it does |
|---|---|
| **CustomParts** | Adds new GPU parts with their own 3D model. Each part gets its own Addressables key mapped to a stock base prefab, and the model is swapped in on spawn. Includes an in-game tuner (F8) with per-motherboard fit saved to `builds.txt`. See `mod/CustomParts/README.md`. |
| **VersionProxy** | A complete `version.dll` proxy (all 17 exports, forwarded to System32). It loads the XML Part Loader from `xpl_version.dll`. The XML Part Loader's own proxy lacks `GetFileVersionInfoExW`, so NVIDIA's NGX fails to load and the game greys out DLSS. This fixes that. |
| **SocketLabels** | Labels PCBS2.SocketLoader's custom sockets (e.g. `100 = sTR5`) in the shop's socket filter. |
| **WindowedRefresh** | Raises the frame cap to the monitor's refresh rate in windowed and borderless modes. Optional override in `Mods\WindowedRefresh.txt` (0 = uncapped). |
| **DlssProbe** | Diagnostic: logs each step of HDRP's DLSS setup. |
| **CustomModels** | Earlier model-swap prototype (superseded by CustomParts). |

## Tools (`tools/`)

Python scripts for generating XML part files from the game's own data, and `customparts_gui.py`, a drag-and-drop GUI that turns a `.glb` or `.blend` model into a CustomParts entry. Run with `uv run --no-project --with UnityPy tools/<script>.py`.

## Building

- C# mods: `dotnet build mod/<Mod>/<Mod>.csproj -c Release`. Set `GameDir` in the `.csproj` to your game folder; it references MelonLoader's generated `Il2CppAssemblies`.
- VersionProxy: `zig cc -target x86_64-windows-gnu -shared -O2 -s -o version.dll version.c version.def -lkernel32`.
  Install: rename the XML Part Loader's `version.dll` to `xpl_version.dll`, then copy this `version.dll` into the game folder.
- CustomParts bundles: `tools/build_customparts.ps1` (needs Unity 6000.2.6f2).

## Not included

The repository doesn't include third-party 3D models, the game's data, or generated part files, because they aren't ours to redistribute. Get models from their authors and convert them with `customparts_gui.py`. Generate part data from your own copy of the game.

## License

Apache License 2.0. See `LICENSE`. This license covers only the code in this repository.
