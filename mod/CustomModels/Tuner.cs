using System;
using System.Globalization;
using System.IO;
using System.Linq;
using UnityEngine;

namespace CustomModels
{
    /// <summary>
    /// In-game tuner for a swap's offset and rotation. F8 shows the panel; keys only act while it's shown.
    ///   arrows: X / Z   PgUp/PgDn: Y   Shift + those: yaw / pitch / roll
    ///   [ ]: step size  F7: next model  F9: save to models.txt
    /// Offsets apply instantly; rotation re-fits the model on the next scan (under a second).
    /// </summary>
    public partial class CustomModelsMod
    {
        static readonly float[] MoveSteps = { 0.001f, 0.01f, 0.1f };
        static readonly float[] TurnSteps = { 1f, 5f, 90f };
        bool panel, guiBroken;
        int step = 1, selected;
        string status = "";

        Swap Selected => swaps.Count == 0 ? null : swaps[selected % swaps.Count];

        void Tune()
        {
            if (Input.GetKeyDown(KeyCode.F8)) panel = !panel;
            var s = Selected;
            if (!panel || s == null) return;
            if (Input.GetKeyDown(KeyCode.F7)) selected = (selected + 1) % swaps.Count;
            if (Input.GetKeyDown(KeyCode.LeftBracket)) step = Math.Max(0, step - 1);
            if (Input.GetKeyDown(KeyCode.RightBracket)) step = Math.Min(MoveSteps.Length - 1, step + 1);
            if (Input.GetKeyDown(KeyCode.F9)) Save(s);

            int dx = Key(KeyCode.RightArrow) - Key(KeyCode.LeftArrow);
            int dz = Key(KeyCode.UpArrow) - Key(KeyCode.DownArrow);
            int dy = Key(KeyCode.PageUp) - Key(KeyCode.PageDown);
            if (dx == 0 && dy == 0 && dz == 0) return;

            if (Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift))
            {
                // Euler is stored as (pitch, yaw, roll).
                float t = TurnSteps[step];
                s.Euler += new Vector3(dz * t, dx * t, dy * t);
                Unplace(p => p.Swap == s);
            }
            else
            {
                var delta = new Vector3(dx, dy, dz) * MoveSteps[step];
                s.Offset += delta;
                foreach (var p in placed.Where(p => p.Swap == s && p.Model != null))
                {
                    p.Model.localPosition = p.Base + s.Offset;
                    var world = p.Holder.transform.TransformVector(delta);
                    foreach (var m in p.Moved) if (m != null) m.position += world;
                }
            }
            status = "";
            if (guiBroken) LoggerInstance.Msg($"{s.Prefab}: offset {s.Offset} rotation(p,y,r) {s.Euler}");
        }

        static int Key(KeyCode k) => Input.GetKeyDown(k) ? 1 : 0;

        // Rewrite this swap's rotation/offset field in models.txt, leaving every other line as is.
        void Save(Swap s)
        {
            var ci = CultureInfo.InvariantCulture;
            string F(float v) => v.ToString("0.###", ci);
            var field = $"{F(s.Euler.y)} {F(s.Euler.x)} {F(s.Euler.z)}  {F(s.Offset.x)} {F(s.Offset.y)} {F(s.Offset.z)}";
            var lines = File.ReadAllLines(cfgPath);
            for (int i = 0; i < lines.Length; i++)
            {
                if (lines[i].TrimStart().StartsWith("#")) continue;
                var p = lines[i].Split('|');
                if (p.Length < 4 || p[0].Trim() != s.Bundle || p[1].Trim() != s.Prefab || p[2].Trim() != s.RootPrefix) continue;
                if (p.Length == 4) Array.Resize(ref p, 5);
                p[4] = field;
                lines[i] = string.Join(" | ", p.Select(x => x?.Trim()));
            }
            File.WriteAllLines(cfgPath, lines);
            cfgTime = File.GetLastWriteTimeUtc(cfgPath); // our own write; don't reload from it
            status = "saved";
            LoggerInstance.Msg($"Saved {s.Prefab}: {field}");
        }

        public override void OnGUI()
        {
            var s = Selected;
            if (!panel || guiBroken || s == null) return;
            try
            {
                var e = s.Euler; var o = s.Offset;
                GUI.Box(new Rect(10, 10, 330, 150), "CustomModels tuner (F8)");
                GUI.Label(new Rect(20, 35, 310, 120),
                    $"{s.Prefab} -> {s.RootPrefix}   (F7 next)\n" +
                    $"offset  x {o.x:0.###}  y {o.y:0.###}  z {o.z:0.###}\n" +
                    $"rotate  yaw {e.y:0.#}  pitch {e.x:0.#}  roll {e.z:0.#}\n" +
                    $"step {MoveSteps[step]} / {TurnSteps[step]}°   [ ] change\n" +
                    $"arrows X/Z, PgUp/PgDn Y, Shift = rotate\n" +
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
