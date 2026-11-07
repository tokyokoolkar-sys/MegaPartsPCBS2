using System;
using System.Globalization;
using System.IO;
using System.Linq;
using UnityEngine;

namespace CustomParts
{
    /// <summary>
    /// In-game tuner for a part's fine offset (parts.txt field 14, mm) and extra rotation (field 15, degrees),
    /// both along the card's own axes. F8 shows the panel; keys only act while it's shown.
    ///   Left/Right: length (+ toward bracket)   Up/Down: height (+ toward power-connector edge)
    ///   PgUp/PgDn: thickness (+ toward the fans)   Shift + those: rotate instead
    ///   [ ]: step size   F9: save to parts.txt
    /// The part tuned is the custom part under the mouse, else the one last spawned.
    /// Every placed copy of the part refits immediately.
    /// </summary>
    public partial class CustomPartsMod
    {
        static readonly float[] Steps = { 0.1f, 0.5f, 2f };
        static readonly float[] TurnSteps = { 1f, 5f, 90f };
        bool panel, guiBroken, quiet;
        int step = 1;
        string status = "";

        Part current;
        Transform currentRoot;
        Part Selected => current ?? fitted.LastOrDefault(x => x.Root != null).Part ?? parts.FirstOrDefault();
        Transform SelectedRoot => currentRoot != null ? currentRoot : fitted.LastOrDefault(x => x.Root != null && x.Part == Selected).Root;
        // Installed card: tune this case + motherboard only (builds.txt). Otherwise the part default (parts.txt).
        string SelectedBuild => BuildOf(SelectedRoot);

        // The custom part under the mouse cursor, if any (raycast against the part colliders).
        void PickUnderMouse()
        {
            var cam = Camera.main;
            if (cam == null) return;
            if (!Physics.Raycast(cam.ScreenPointToRay(Input.mousePosition), out var hit, 50f)) return;
            for (var t = hit.collider.transform; t != null; t = t.parent)
            {
                var p = parts.FirstOrDefault(x => x.Id == t.name);
                if (p != null) { current = p; currentRoot = t; return; }
            }
        }

        void Tune()
        {
            if (Input.GetKeyDown(KeyCode.F8)) panel = !panel;
            if (!panel) return;
            PickUnderMouse();
            var p = Selected;
            if (p == null) return;
            if (Input.GetKeyDown(KeyCode.LeftBracket)) step = Math.Max(0, step - 1);
            if (Input.GetKeyDown(KeyCode.RightBracket)) step = Math.Min(Steps.Length - 1, step + 1);
            if (Input.GetKeyDown(KeyCode.F9)) Save(p);

            var d = new Vector3(Key(KeyCode.RightArrow) - Key(KeyCode.LeftArrow),
                                Key(KeyCode.UpArrow) - Key(KeyCode.DownArrow),
                                Key(KeyCode.PageUp) - Key(KeyCode.PageDown));
            if (d == Vector3.zero) return;
            // Shift: rotate about the card's length (Up/Down), height (Left/Right) and thickness (PgUp/PgDn) axes.
            var build = SelectedBuild;
            var (o, r, _) = Tuning(p, build);
            if (Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift))
                r = Wrap(r + new Vector3(d.y, d.x, d.z) * TurnSteps[step]);
            else
                o += d * Steps[step];
            if (build != null) p.Builds[build] = (o, r); else (p.OffsetMm, p.RotDeg) = (o, r);
            quiet = true;
            try { Refit((x, root) => x == p && BuildOf(root) == build); } finally { quiet = false; }
            status = "";
            if (guiBroken) LoggerInstance.Msg($"[{p.Id}] {build ?? "default"}: offset mm {Fmt(o)}, rotation deg {Fmt(r)}");
        }

        static Vector3 Wrap(Vector3 v) { for (int i = 0; i < 3; i++) v[i] = Mathf.Repeat(v[i] + 180f, 360f) - 180f; return v; }
        static int Key(KeyCode k) => Input.GetKeyDown(k) ? 1 : 0;
        static string Fmt(Vector3 v) => string.Join(" ", new[] { v.x, v.y, v.z }.Select(x => x.ToString("0.##", CultureInfo.InvariantCulture)));

        // Rewrite this part's offset and rotation fields in parts.txt, leaving every other line as is.
        void Save(Part p)
        {
            var build = SelectedBuild;
            if (build != null)
            {
                if (!p.Builds.ContainsKey(build)) { var (o0, r0, _) = Tuning(p, build); p.Builds[build] = (o0, r0); }
                SaveBuilds();
                status = "saved for this build";
                LoggerInstance.Msg($"[{p.Id}] saved for {build}: offset mm {Fmt(p.Builds[build].Off)}, rotation deg {Fmt(p.Builds[build].Rot)}");
                return;
            }
            var lines = File.ReadAllLines(cfgPath);
            for (int i = 0; i < lines.Length; i++)
            {
                if (lines[i].TrimStart().StartsWith("#")) continue;
                var f = lines[i].Split('|');
                if (f.Length < 11 || f[0].Trim() != p.Id) continue;
                if (f.Length < 15) Array.Resize(ref f, 15);
                f[13] = Fmt(p.OffsetMm);
                f[14] = Fmt(p.RotDeg);
                lines[i] = string.Join(" | ", f.Select(x => x?.Trim() ?? ""));
            }
            File.WriteAllLines(cfgPath, lines);
            cfgTime = File.GetLastWriteTimeUtc(cfgPath); // our own write; don't reload from it
            status = "saved";
            LoggerInstance.Msg($"[{p.Id}] saved offset mm {Fmt(p.OffsetMm)}, rotation deg {Fmt(p.RotDeg)}");
        }

        public override void OnGUI()
        {
            var p = Selected;
            if (!panel || guiBroken || p == null) return;
            try
            {
                var build = SelectedBuild;
                var (o, r, own) = Tuning(p, build);
                GUI.Box(new Rect(10, 10, 440, 205), "CustomParts tuner (F8)");
                GUI.Label(new Rect(20, 35, 420, 180),
                    $"{p.Id}   (part under mouse / last spawned)\n" +
                    (build != null ? $"in slot, tuning this build{(own ? "" : " (from default)")}: {build}\n" : "not in a slot, tuning the part default\n") +
                    $"offset mm    length {o.x:0.##}  height {o.y:0.##}  thick {o.z:0.##}\n" +
                    $"rotate deg   length {r.x:0.#}  height {r.y:0.#}  thick {r.z:0.#}\n" +
                    $"step {Steps[step]} mm / {TurnSteps[step]} deg   [ ] change\n" +
                    $"Left/Right length, Up/Down height, PgUp/PgDn thickness\n" +
                    $"Shift + keys: rotate about Up/Down length, Left/Right height, PgUp/PgDn thickness\n" +
                    $"F9 save {status}");
            }
            catch (Exception ex)
            {
                // IMGUI may be stripped from the game; keys still work, values go to the log.
                guiBroken = true;
                LoggerInstance.Warning($"Panel unavailable ({ex.GetType().Name}); tuner values are logged instead");
            }
        }
    }
}
