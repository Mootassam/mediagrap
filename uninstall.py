r"""MediaGrab uninstaller — runs under the bundled, digitally signed Python runtime.

Windows Smart App Control blocks Inno Setup's generated, unsigned ``unins000.exe``. The embedded
Python runtime shipped with the app *is* signed (Python Software Foundation), so SAC allows it —
this script does the same job: stop the app, remove shortcuts and the Apps-list entry, then delete
the program folder.

Your downloaded files are never touched. Settings and download history (in %LOCALAPPDATA%\MediaGrab)
are only deleted if you say Yes.

Usage (wired up by the installer):
    pythonw.exe uninstall.py           # asks, shows result
    python.exe  uninstall.py /quiet     # no prompts, keeps settings (used for silent uninstalls)
"""

from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
import tempfile

APP_NAME = "MediaGrab"
APPID_KEY = "{5E1B7C42-9D3A-4C6E-8F21-MEDIAGRAB0001}_is1"
HERE = os.path.dirname(os.path.abspath(__file__))        # ...\MediaGrab\app
INSTALL_DIR = os.path.dirname(HERE)                       # ...\MediaGrab
QUIET = any(a.lower() in ("/quiet", "/silent", "/verysilent", "-q") for a in sys.argv[1:])

MB_YESNO, MB_ICONQUESTION, MB_ICONINFO, MB_DEFBUTTON2 = 0x4, 0x20, 0x40, 0x100
IDYES = 6


def _msg(text: str, title: str = APP_NAME, flags: int = MB_ICONINFO, quiet_answer: int = IDYES) -> int:
    if QUIET:
        return quiet_answer
    try:
        return ctypes.windll.user32.MessageBoxW(0, text, title, flags | 0x10000)  # MB_SETFOREGROUND
    except Exception:
        return quiet_answer


def _data_dir() -> str:
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return os.path.join(base, APP_NAME)


def _downloads_dir() -> str:
    try:
        import json
        with open(os.path.join(_data_dir(), "settings.json"), encoding="utf-8") as f:
            d = json.load(f).get("download_dir")
            if d:
                return d
    except Exception:
        pass
    return os.path.join(os.path.expanduser("~"), "Downloads", APP_NAME)


def _kill_under(folder: str) -> None:
    """Terminate every process whose executable lives inside *folder* (except ourselves)."""
    import ctypes.wintypes as wt

    folder_l = os.path.normcase(os.path.abspath(folder))
    me = os.getpid()
    k32 = ctypes.windll.kernel32

    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [
            ("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ProcessID", wt.DWORD),
            ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)), ("th32ModuleID", wt.DWORD),
            ("cntThreads", wt.DWORD), ("th32ParentProcessID", wt.DWORD), ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", wt.DWORD), ("szExeFile", ctypes.c_wchar * 260),
        ]

    snap = k32.CreateToolhelp32Snapshot(0x2, 0)
    if snap == -1:
        return
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        ok = k32.Process32FirstW(snap, ctypes.byref(entry))
        while ok:
            pid = entry.th32ProcessID
            if pid and pid != me and entry.szExeFile.lower() in ("python.exe", "pythonw.exe", "deno.exe"):
                h = k32.OpenProcess(0x1000, False, pid)
                if h:
                    buf = ctypes.create_unicode_buffer(32768)
                    size = wt.DWORD(len(buf))
                    path = buf.value if k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)) else ""
                    k32.CloseHandle(h)
                    if path and os.path.normcase(os.path.abspath(path)).startswith(folder_l):
                        ht = k32.OpenProcess(0x1, False, pid)
                        if ht:
                            k32.TerminateProcess(ht, 0)
                            k32.CloseHandle(ht)
            ok = k32.Process32NextW(snap, ctypes.byref(entry))
    finally:
        k32.CloseHandle(snap)


def _remove_shortcuts() -> None:
    lnks = []
    for env in ("USERPROFILE", "OneDrive", "OneDriveConsumer", "PUBLIC"):
        base = os.environ.get(env)
        if base:
            lnks.append(os.path.join(base, "Desktop", f"{APP_NAME}.lnk"))
    appdata = os.environ.get("APPDATA")
    if appdata:
        programs = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs")
        lnks += [os.path.join(programs, f"{APP_NAME}.lnk"), os.path.join(programs, f"Uninstall {APP_NAME}.lnk")]
        shutil.rmtree(os.path.join(programs, APP_NAME), ignore_errors=True)
    for lnk in lnks:
        try:
            if os.path.exists(lnk):
                os.remove(lnk)
        except Exception:
            pass


def _remove_registry() -> None:
    try:
        import winreg
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion\Uninstall" + "\\" + APPID_KEY)
    except Exception:
        pass


def _schedule_dir_delete(folder: str) -> None:
    """Delete the install folder after we exit (our own python.exe lives in it).
    cmd.exe is signed by Microsoft, so Smart App Control allows it."""
    bat = os.path.join(tempfile.gettempdir(), "mediagrab_uninstall_cleanup.bat")
    script = (
        "@echo off\r\n"
        "set n=0\r\n"
        ":retry\r\n"
        "ping -n 2 127.0.0.1 >nul\r\n"
        'rmdir /s /q "%s" 2>nul\r\n'
        'if not exist "%s" goto done\r\n'
        "set /a n+=1\r\n"
        "if %%n%% lss 60 goto retry\r\n"
        ":done\r\n"
        'del "%%~f0"\r\n'
    ) % (folder, folder)
    try:
        with open(bat, "w", encoding="mbcs") as fh:
            fh.write(script)
        subprocess.Popen(["cmd.exe", "/c", bat], creationflags=0x8 | 0x8000000, close_fds=True)
    except Exception:
        pass


def main() -> int:
    if _msg(f"Uninstall {APP_NAME}?\n\nYour downloaded videos, music and images are NOT deleted — "
            f"they stay in:\n{_downloads_dir()}",
            f"Uninstall {APP_NAME}", MB_YESNO | MB_ICONQUESTION) != IDYES:
        return 1

    _kill_under(INSTALL_DIR)
    _remove_shortcuts()
    _remove_registry()

    removed_data = False
    if os.path.isdir(_data_dir()):
        if _msg("Also delete your MediaGrab settings and download history?\n\n"
                "Your downloaded files are not affected either way.\n\n"
                "Choose No to keep your settings for a future reinstall.",
                f"Uninstall {APP_NAME}", MB_YESNO | MB_ICONQUESTION | MB_DEFBUTTON2, quiet_answer=7) == IDYES:
            shutil.rmtree(_data_dir(), ignore_errors=True)
            removed_data = True

    _schedule_dir_delete(INSTALL_DIR)
    _msg(f"{APP_NAME} has been uninstalled.\n\n"
         + ("Settings and history were deleted. " if removed_data else "Your settings and history were kept. ")
         + f"Your downloads are still in:\n{_downloads_dir()}",
         f"{APP_NAME} uninstalled", MB_ICONINFO)
    return 0


if __name__ == "__main__":
    sys.exit(main())
