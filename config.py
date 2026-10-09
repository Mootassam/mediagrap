"""User settings, stored as JSON in the data folder."""

from __future__ import annotations

import json
import os
import threading

import app_paths

DEFAULTS = {
    "download_dir": app_paths.default_download_dir(),
    "concurrency": 2,                 # simultaneous downloads
    "fragments": 4,                   # parallel fragments per HLS/DASH download
    "container": "mp4",               # mp4 | mkv
    "compat": True,                   # prefer H.264/AAC so files play everywhere
    "default_quality": "best",        # best | 2160 | 1440 | 1080 | 720 | 480 | 360 | audio
    "embed_metadata": True,
    "embed_thumbnail": True,
    "embed_subs": False,
    "sub_langs": "en",
    "subfolder_by_site": True,        # Downloads/MediaGrab/YouTube/...
    "playlist_subfolder": True,
    "filename": "%(title).150B [%(id)s].%(ext)s",
    "cookies_browser": "",            # "" | chrome | edge | firefox | brave | opera | vivaldi
    "cookies_file": "",
    "rate_limit": "",                 # e.g. "5M" (bytes/s), empty = unlimited
    "proxy": "",
    "auto_retry": 3,                  # whole-job retries after a network failure
    "theme": "auto",
}

_LOCK = threading.Lock()
_cache: dict | None = None


def _path() -> str:
    return os.path.join(app_paths.data_dir(), "settings.json")


def load() -> dict:
    global _cache
    with _LOCK:
        if _cache is None:
            data = {}
            try:
                with open(_path(), encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
            _cache = {**DEFAULTS, **{k: v for k, v in data.items() if k in DEFAULTS}}
        return dict(_cache)


def save(patch: dict) -> dict:
    global _cache
    cur = load()
    for k, v in (patch or {}).items():
        if k not in DEFAULTS:
            continue
        d = DEFAULTS[k]
        if isinstance(d, bool):
            v = bool(v)
        elif isinstance(d, int):
            try:
                v = int(v)
            except (TypeError, ValueError):
                continue
        else:
            v = "" if v is None else str(v).strip()
        cur[k] = v
    cur["concurrency"] = max(1, min(6, cur["concurrency"]))
    cur["fragments"] = max(1, min(16, cur["fragments"]))
    cur["auto_retry"] = max(0, min(10, cur["auto_retry"]))
    if not cur["download_dir"]:
        cur["download_dir"] = app_paths.default_download_dir()
    with _LOCK:
        _cache = cur
        tmp = _path() + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cur, f, indent=2)
        os.replace(tmp, _path())
    return dict(cur)
