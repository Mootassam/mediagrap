"""Locate helper programs (ffmpeg, deno) and report / update engine versions."""

from __future__ import annotations

import importlib.metadata as md
import os
import shutil
import subprocess
import sys

import app_paths

NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def _bundled(name: str) -> str | None:
    p = os.path.join(app_paths.resource_dir(), "bin", name + (".exe" if os.name == "nt" else ""))
    return p if os.path.isfile(p) else None


def ffmpeg_dir() -> str | None:
    """Folder holding ffmpeg + ffprobe (yt-dlp needs both to merge/convert)."""
    p = _bundled("ffmpeg") or shutil.which("ffmpeg")
    if not p:
        # winget installs ffmpeg under the user's WinGet packages folder
        base = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages")
        if os.path.isdir(base):
            for root, _dirs, files in os.walk(base):
                if "ffmpeg.exe" in files and "ffprobe.exe" in files:
                    p = os.path.join(root, "ffmpeg.exe")
                    break
    return os.path.dirname(p) if p else None


def deno_path() -> str | None:
    """JavaScript runtime yt-dlp uses to solve YouTube's signature challenges."""
    p = _bundled("deno")
    if p:
        return p
    try:
        import deno  # pip package that ships the official deno binary
        p = deno.find_deno_bin()
        if p and os.path.isfile(p):
            return p
    except Exception:
        pass
    return shutil.which("deno")


def js_runtimes() -> dict:
    d = deno_path()
    if d:
        return {"deno": {"path": d}}
    node = shutil.which("node")
    return {"node": {"path": node}} if node else {"deno": {}}


def _ver(pkg: str) -> str:
    try:
        return md.version(pkg)
    except Exception:
        return ""


def status() -> dict:
    ff = ffmpeg_dir()
    return {
        "yt_dlp": _ver("yt-dlp"),
        "gallery_dl": _ver("gallery-dl"),
        "ejs": _ver("yt-dlp-ejs"),
        "ffmpeg": bool(ff),
        "ffmpeg_dir": ff or "",
        "deno": bool(deno_path()),
        "python": sys.version.split()[0],
    }


def update_engines() -> tuple[bool, str]:
    """Upgrade the download engines in place (sites change often; this fixes most breakages)."""
    py = sys.executable
    if os.path.basename(py).lower() == "pythonw.exe":
        py = os.path.join(os.path.dirname(py), "python.exe")
    if app_paths.is_installed():
        # installed app: replace only the pure-Python engines (native libraries in use stay untouched)
        site = os.path.join(os.path.dirname(sys.executable), "Lib", "site-packages")
        cmd = [py, "-m", "pip", "install", "--upgrade", "--no-deps", "--disable-pip-version-check",
               "--no-cache-dir", "--only-binary=:all:", "--target", site,
               "yt-dlp", "yt-dlp-ejs", "gallery-dl"]
    else:
        cmd = [py, "-m", "pip", "install", "--upgrade", "--disable-pip-version-check",
               "--no-cache-dir", "yt-dlp[default,curl-cffi]", "yt-dlp-ejs", "gallery-dl"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, creationflags=NO_WINDOW)
    except Exception as e:  # noqa: BLE001
        return False, str(e)
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode == 0:
        out += "\nRestart MediaGrab to use the new engine version."
    return r.returncode == 0, out[-3000:]


def install_ffmpeg() -> tuple[bool, str]:
    """Install FFmpeg with Windows' own package manager (winget) — signed, trusted builds."""
    winget = shutil.which("winget") or os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft",
                                                     "WindowsApps", "winget.exe")
    if not os.path.isfile(winget):
        return False, "winget isn't available on this PC. Install FFmpeg from https://www.gyan.dev/ffmpeg/builds/"
    cmd = [winget, "install", "--id", "Gyan.FFmpeg", "-e", "--silent", "--accept-source-agreements",
           "--accept-package-agreements", "--disable-interactivity"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=900, creationflags=NO_WINDOW)
    except Exception as e:  # noqa: BLE001
        return False, str(e)
    out = ((r.stdout or "") + (r.stderr or "")).replace("\r", "")
    out = "\n".join(l for l in out.split("\n") if l.strip() and not set(l.strip()) <= set("-\\|/█▒ "))
    return bool(ffmpeg_dir()), out[-2500:]
