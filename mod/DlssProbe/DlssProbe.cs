using System;
using MelonLoader;
using UnityEngine;
using UnityEngine.NVIDIA;

[assembly: MelonInfo(typeof(DlssProbe.Probe), "DlssProbe", "0.1.0", "MegaParts")]
[assembly: MelonGame]

namespace DlssProbe
{
    // Diagnostic only: logs each step of HDRP's DLSSPass.SetupFeature so we can see which one fails.
    public class Probe : MelonMod
    {
        bool done;

        public override void OnSceneWasLoaded(int buildIndex, string sceneName)
        {
            if (done) return;
            done = true;
            Step("graphics API", () => SystemInfo.graphicsDeviceType.ToString());
            Step("vendor", () => SystemInfo.graphicsDeviceVendor + " / driver " + SystemInfo.graphicsDeviceVersion);
            Step("NVUnityPlugin.IsLoaded", () => NVUnityPlugin.IsLoaded().ToString());
            Step("GraphicsDevice.version", () => GraphicsDevice.version.ToString());
            Step("HDRP DLSSDetected", () => UnityEngine.Rendering.HighDefinition.HDDynamicResolutionPlatformCapabilities.DLSSDetected.ToString());
            Step("GraphicsDevice.device (existing)", () => GraphicsDevice.device == null ? "null" : "present");
            GraphicsDevice dev = null;
            Step("CreateGraphicsDevice", () => { dev = GraphicsDevice.CreateGraphicsDevice(); return dev == null ? "null (NGX init failed)" : "ok"; });
            if (dev != null)
            {
                Step("IsFeatureAvailable(DLSS)", () => dev.IsFeatureAvailable(GraphicsDeviceFeature.DLSS).ToString());
            }
        }

        void Step(string what, Func<string> f)
        {
            try { LoggerInstance.Msg($"{what}: {f()}"); }
            catch (Exception e) { LoggerInstance.Error($"{what}: threw {e.GetType().Name}: {e.Message}"); }
        }
    }
}
