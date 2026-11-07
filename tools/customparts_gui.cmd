@echo off
rem Opens the CustomParts GUI (drag and drop a .glb, fill in the card, Build, Deploy).
cd /d "%~dp0.."
uv run --no-project --with tkinterdnd2 tools\customparts_gui.py
