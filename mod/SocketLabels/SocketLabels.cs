using System.Collections.Generic;
using System.IO;
using HarmonyLib;
using Il2CppI2.Loc;
using MelonLoader;
using MelonLoader.Utils;

[assembly: MelonInfo(typeof(SocketLabels.Mod), "SocketLabels", "0.1.0", "MegaParts")]
[assembly: MelonGame]

namespace SocketLabels
{
    // The shop's socket filter labels each socket with the translation "Sockets/" + socket.ToString().
    // SocketLoader's custom sockets are numbers outside the CpuSocket enum (e.g. 100 = sTR5), so the key is
    // "Sockets/100", which has no translation, and the filter drops the entry. This supplies those labels
    // from SocketLoader's sockets.ini.
    public class Mod : MelonMod
    {
        static readonly Dictionary<string, string> Labels = new();

        public override void OnInitializeMelon()
        {
            var ini = Path.Combine(MelonEnvironment.GameRootDirectory, "addons", "PCBS2.SocketLoader", "sockets.ini");
            if (!File.Exists(ini)) { LoggerInstance.Warning($"no {ini}"); return; }
            foreach (var raw in File.ReadAllLines(ini))
            {
                var line = raw.Split(';', '#')[0];
                var eq = line.IndexOf('=');
                if (eq < 0) continue;
                var id = line[..eq].Trim();
                var name = line[(eq + 1)..].Trim();
                if (int.TryParse(id, out _) && name.Length > 0) Labels["Sockets/" + id] = name;
            }
            LoggerInstance.Msg($"{Labels.Count} socket label(s): {string.Join(", ", Labels.Values)}");
        }

        [HarmonyPatch(typeof(LocalizationManager), nameof(LocalizationManager.GetTranslation),
            new[] { typeof(string), typeof(bool), typeof(int), typeof(bool), typeof(bool), typeof(UnityEngine.GameObject), typeof(string) })]
        static class GetTranslationPatch
        {
            static void Postfix(string __0, ref string __result)
            {
                if (string.IsNullOrEmpty(__result) && __0 != null && Labels.TryGetValue(__0, out var label)) __result = label;
            }
        }
    }
}
