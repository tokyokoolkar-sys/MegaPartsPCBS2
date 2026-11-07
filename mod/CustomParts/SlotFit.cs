using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

namespace CustomParts
{
    /// <summary>
    /// v2.1 per-build tuning. The game snaps every card to its slot at one fixed pose (measured identical
    /// across cases and slots), and motherboards are single merged meshes, so there is no slot geometry
    /// to align to; the remaining shift comes from each motherboard model (same board in another case fits the
    /// same). So tuning saved (F9) while a card is installed is stored per motherboard in builds.txt, starting from the
    /// part default, and is applied whenever the card is in that build. Cards refit on install / move.
    /// </summary>
    public partial class CustomPartsMod
    {
        // Fitted root -> (slot it was fitted in, build key), to refit when the card is installed or moved.
        readonly Dictionary<int, (int Slot, string Build)> fittedSlot = new();
        string buildsPath;

        static Il2Cpp.Slot SlotOf(Transform root)
        {
            try
            {
                var s = root.GetComponent<Il2Cpp.ComponentPC>()?.Slot;
                return s != null && s.m_slotType == Il2Cpp.Slot.SlotType.PCI ? s : null;
            }
            catch { return null; }
        }

        static string BuildKey(Il2Cpp.Slot slot)
        {
            if (slot == null) return null;
            try
            {
                var mobo = Parents(slot.transform).Select(t => t.GetComponent<Il2Cpp.ComponentPC>()).FirstOrDefault(c => c != null);
                // Keyed on the motherboard only: the fit was tested identical across cases on the same board.
                return mobo != null ? mobo.gameObject.name : null;
            }
            catch { return null; }
        }

        static IEnumerable<Transform> Parents(Transform t) { for (t = t?.parent; t != null; t = t.parent) yield return t; }

        (Vector3 Off, Vector3 Rot, bool Own) Tuning(Part p, string build) =>
            build != null && p.Builds.TryGetValue(build, out var b) ? (b.Off, b.Rot, true) : (p.OffsetMm, p.RotDeg, false);

        // Once a second: refit cards that were installed, removed or moved since they were fitted.
        void CheckSlots()
        {
            var changed = new HashSet<int>();
            foreach (var (_, root, _) in fitted)
            {
                if (root == null) continue;
                var s = SlotOf(root);
                int id = s == null ? 0 : s.GetInstanceID();
                if (fittedSlot.TryGetValue(root.GetInstanceID(), out var was) && was.Slot != id) changed.Add(root.GetInstanceID());
            }
            if (changed.Count > 0) Refit((_, r) => changed.Contains(r.GetInstanceID()));
        }

        // The build key of a fitted card (null when it isn't in a slot).
        string BuildOf(Transform root) => root != null && fittedSlot.TryGetValue(root.GetInstanceID(), out var v) ? v.Build : null;

        // builds.txt: part ID | motherboard | offset mm | rotation deg
        void LoadBuilds()
        {
            if (!File.Exists(buildsPath)) return;
            foreach (var raw in File.ReadAllLines(buildsPath))
            {
                var line = raw.Trim();
                if (line.Length == 0 || line.StartsWith("#")) continue;
                var f = line.Split('|').Select(x => x.Trim()).ToArray();
                var p = parts.FirstOrDefault(x => x.Id == f[0]);
                if (p == null || f.Length < 3) continue;
                try { p.Builds[f[1]] = (Offset(f, 2), Offset(f, 3)); }
                catch (Exception ex) { LoggerInstance.Warning($"builds.txt: {ex.Message}: {line}"); }
            }
            LoggerInstance.Msg($"builds.txt: {parts.Sum(x => x.Builds.Count)} build tuning(s)");
        }

        void SaveBuilds()
        {
            var lines = new List<string>
            {
                "# CustomParts per-build tuning, written by the F8 tuner (F9 while the card is installed).",
                "# part ID | motherboard | offset mm (length height thickness) | rotation deg",
            };
            foreach (var p in parts) foreach (var (k, v) in p.Builds) lines.Add($"{p.Id} | {k} | {Fmt(v.Off)} | {Fmt(v.Rot)}");
            File.WriteAllLines(buildsPath, lines);
        }
    }
}
