using HarmonyLib;
using MelonLoader;
using UnityEngine;

[assembly: MelonInfo(typeof(WindowedRefresh.Mod), "WindowedRefresh", "0.1.0", "MegaParts")]
[assembly: MelonGame]

namespace WindowedRefresh
{
    // The game sets Application.targetFrameRate in GameController.ApplyVSync from its refresh-rate setting,
    // which the options menu locks in windowed / borderless. This raises the cap to the monitor's real rate
    // (e.g. 200 Hz) in every window mode. Override with Mods\WindowedRefresh.txt holding a number (0 = uncapped).
    public class Mod : MelonMod
    {
        static int Override = -1;

        public override void OnInitializeMelon()
        {
            var f = System.IO.Path.Combine(MelonLoader.Utils.MelonEnvironment.ModsDirectory, "WindowedRefresh.txt");
            if (System.IO.File.Exists(f) && int.TryParse(System.IO.File.ReadAllText(f).Trim(), out var v)) Override = v;
        }

        internal static void Apply()
        {
            int hz = Override >= 0 ? Override : Mathf.RoundToInt((float)Screen.currentResolution.refreshRateRatio.value);
            int target = hz == 0 ? -1 : hz;
            int cur = Application.targetFrameRate;
            if (Override < 0 && (cur <= 0 || cur >= target)) return; // never lower what the game chose (or uncapped)
            Application.targetFrameRate = target;
            Melon<Mod>.Logger.Msg($"frame cap -> {(target < 0 ? "uncapped" : target + " fps")} (mode {Screen.fullScreenMode}, vSync {QualitySettings.vSyncCount})");
        }

        [HarmonyPatch(typeof(Il2Cpp.GameController), nameof(Il2Cpp.GameController.ApplyVSync))]
        static class ApplyVSyncPatch
        {
            static void Postfix() => Apply();
        }
    }
}
