// Full version.dll proxy for PCBS2.
// The XML Part Loader ships as a version.dll proxy that only exports 6 of the 17 functions. NVIDIA's NGX
// loader (_nvngx.dll) needs GetFileVersionInfoExW, finds the game-folder version.dll first, fails to load,
// and Unity reports DLSS as unavailable. This proxy forwards all 17 exports to the real System32 version.dll
// and then loads the XML Part Loader from xpl_version.dll, so both DLSS and XML parts work.
#include <windows.h>

#define FUNCS(X) \
    X(GetFileVersionInfoA) X(GetFileVersionInfoByHandle) X(GetFileVersionInfoExA) X(GetFileVersionInfoExW) \
    X(GetFileVersionInfoSizeA) X(GetFileVersionInfoSizeExA) X(GetFileVersionInfoSizeExW) X(GetFileVersionInfoSizeW) \
    X(GetFileVersionInfoW) X(VerFindFileA) X(VerFindFileW) X(VerInstallFileA) X(VerInstallFileW) \
    X(VerLanguageNameA) X(VerLanguageNameW) X(VerQueryValueA) X(VerQueryValueW)

#define DECL(n) void *p_##n;
FUNCS(DECL)

// Each export is a bare jump through its pointer, so arguments and return values pass through untouched.
#define STUB(n) __attribute__((naked)) void proxy_##n(void) { __asm__("jmp *p_" #n "(%rip)"); }
FUNCS(STUB)

static void load(void)
{
    wchar_t path[MAX_PATH];
    GetSystemDirectoryW(path, MAX_PATH);
    lstrcatW(path, L"\\version.dll");
    HMODULE real = LoadLibraryW(path);
#define RESOLVE(n) p_##n = (void *)GetProcAddress(real, #n);
    FUNCS(RESOLVE)

    // Then the XML Part Loader, renamed, from the game folder (next to this dll).
    wchar_t xpl[MAX_PATH];
    HMODULE self;
    GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                       (LPCWSTR)&load, &self);
    DWORD n = GetModuleFileNameW(self, xpl, MAX_PATH);
    while (n > 0 && xpl[n - 1] != L'\\') n--;
    xpl[n] = 0;
    lstrcatW(xpl, L"xpl_version.dll");
    if (GetFileAttributesW(xpl) != INVALID_FILE_ATTRIBUTES) LoadLibraryW(xpl);
}

BOOL WINAPI DllMain(HINSTANCE h, DWORD reason, LPVOID r)
{
    if (reason == DLL_PROCESS_ATTACH) { DisableThreadLibraryCalls(h); load(); }
    return TRUE;
}
