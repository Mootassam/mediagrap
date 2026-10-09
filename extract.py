"""
Analyze a link: works out what can be downloaded from it.

yt-dlp handles video/audio for 1800+ sites (YouTube, TikTok, Instagram, X, Facebook,
Vimeo, Reddit, Twitch, SoundCloud...). gallery-dl handles image posts and galleries
(Instagram photos & carousels, X/Twitter images, Pinterest, Reddit, Tumblr, Flickr...).
Both results are merged into one normalized description for the UI.
"""

from __future__ import annotations

import ipaddress
import json
import os
import re
import socket
import subprocess
import sys
import threading
import urllib.parse

import config
import tools

IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".bmp", ".heic", ".jfif")
VID_EXT = (".mp4", ".webm", ".mkv", ".mov", ".m4v", ".avi", ".m3u8", ".mpd", ".mp3", ".m4a", ".ogg", ".wav", ".flac")

# sites where a post can hold photos — also ask gallery-dl so images aren't missed
IMAGE_SITES = ("instagram.com", "twitter.com", "x.com", "pinterest.", "pin.it", "reddit.com", "redd.it",
               "tumblr.com", "flickr.com", "deviantart.com", "imgur.com", "artstation.com", "bsky.app",
               "threads.net", "threads.com", "tiktok.com", "facebook.com", "vk.com", "weibo.")

SITE_NAMES = {
    "youtube": "YouTube", "youtubetab": "YouTube", "tiktok": "TikTok", "tiktokuser": "TikTok",
    "instagram": "Instagram", "instagramstory": "Instagram", "instagramuser": "Instagram",
    "twitter": "X (Twitter)", "facebook": "Facebook", "vimeo": "Vimeo", "reddit": "Reddit",
    "twitch": "Twitch", "twitchvod": "Twitch", "twitchclips": "Twitch", "dailymotion": "Dailymotion",
    "soundcloud": "SoundCloud", "pinterest": "Pinterest", "bilibili": "Bilibili", "kick": "Kick",
    "linkedin": "LinkedIn", "snapchat": "Snapchat", "threads": "Threads", "bluesky": "Bluesky",
    "generic": "Web", "rumble": "Rumble", "vk": "VK", "streamable": "Streamable",
}

QUALITY_BADGE = {4320: "8K", 2160: "4K", 1440: "2K", 1080: "Full HD", 720: "HD", 480: "SD", 360: "Low", 240: "Low", 144: "Tiny"}

AUDIO_CHOICES = [
    ("mp3-320", "MP3", "320 kbps · best for music", 320),
    ("mp3-192", "MP3", "192 kbps · smaller file", 192),
    ("mp3-128", "MP3", "128 kbps · smallest", 128),
    ("m4a", "M4A (AAC)", "Original quality, no re-encode loss", None),
    ("opus", "Opus", "Original quality, very efficient", None),
    ("wav", "WAV", "Uncompressed, for editing", None),
]


class AnalyzeError(Exception):
    pass


# ----------------------------------------------------------------------------- helpers

def normalize_url(url: str) -> str:
    url = (url or "").strip().strip("<>\"'")
    if not url:
        raise AnalyzeError("Paste a link first.")
    if not re.match(r"^[a-z][a-z0-9+.-]*://", url, re.I):
        url = "https://" + url
    p = urllib.parse.urlparse(url)
    if p.scheme not in ("http", "https") or not p.netloc:
        raise AnalyzeError("That doesn't look like a web link.")
    return url


def site_of(url: str) -> str:
    host = urllib.parse.urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def is_public_host(url: str) -> bool:
    """Block localhost / private networks for server-side fetches."""
    host = urllib.parse.urlparse(url).hostname
    if not host:
        return False
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0].split("%")[0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False
    return True


HOST_NAMES = {
    "youtube.com": "YouTube", "youtu.be": "YouTube", "music.youtube.com": "YouTube", "m.youtube.com": "YouTube",
    "tiktok.com": "TikTok", "vm.tiktok.com": "TikTok", "vt.tiktok.com": "TikTok", "instagram.com": "Instagram",
    "twitter.com": "X (Twitter)", "x.com": "X (Twitter)", "facebook.com": "Facebook", "fb.watch": "Facebook",
    "m.facebook.com": "Facebook", "vimeo.com": "Vimeo", "reddit.com": "Reddit", "old.reddit.com": "Reddit",
    "v.redd.it": "Reddit", "twitch.tv": "Twitch", "clips.twitch.tv": "Twitch", "soundcloud.com": "SoundCloud",
    "pinterest.com": "Pinterest", "pin.it": "Pinterest", "dailymotion.com": "Dailymotion", "threads.net": "Threads",
    "threads.com": "Threads", "bsky.app": "Bluesky", "linkedin.com": "LinkedIn", "kick.com": "Kick",
}


def pretty_host(url: str) -> str:
    host = site_of(url).split(":")[0]
    if host in HOST_NAMES:
        return HOST_NAMES[host]
    for h, name in HOST_NAMES.items():
        if host.endswith("." + h):
            return name
    return host


def pretty_site(extractor_key: str, url: str) -> str:
    k = (extractor_key or "").lower()
    if k in SITE_NAMES:
        return SITE_NAMES[k]
    for key, name in SITE_NAMES.items():
        if key != "generic" and k.startswith(key):
            return name
    host = site_of(url)
    return host.split(":")[0] if k in ("", "generic") else (extractor_key or host)


class _QuietLogger:
    def __init__(self):
        self.warnings: list[str] = []

    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        self.warnings.append(str(msg))

    def error(self, msg):
        self.warnings.append(str(msg))


def base_opts(s: dict | None = None) -> dict:
    """yt-dlp options shared by analyze + download."""
    s = s or config.load()
    o = {
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "socket_timeout": 30,
        "retries": 15,
        "extractor_retries": 5,
        "file_access_retries": 10,
        "fragment_retries": 50,
        "retry_sleep_functions": {"http": lambda n: min(2 ** n, 30), "fragment": lambda n: min(2 ** n, 30),
                                  "extractor": lambda n: min(2 ** n, 20)},
        "js_runtimes": tools.js_runtimes(),
        "windowsfilenames": True,
        "trim_file_name": 180,
        "noplaylist": True,
        "ignore_no_formats_error": True,
    }
    ff = tools.ffmpeg_dir()
    if ff:
        o["ffmpeg_location"] = ff
    if s.get("cookies_file") and os.path.isfile(s["cookies_file"]):
        o["cookiefile"] = s["cookies_file"]
    elif s.get("cookies_browser"):
        o["cookiesfrombrowser"] = (s["cookies_browser"],)
    if s.get("proxy"):
        o["proxy"] = s["proxy"]
    return o


def friendly_error(msg: str) -> str:
    m = re.sub(r"\x1b\[[0-9;]*m", "", str(msg or "")).replace("ERROR: ", "").strip()
    low = m.lower()
    if "unsupported url" in low:
        return "This site or link type isn't supported. Try the direct link to the video or post."
    if "login" in low or "log in" in low or "sign in" in low or "cookies" in low or "rate-limit" in low \
            or "authentication" in low:
        return ("This content needs you to be logged in. Open Settings → Login cookies and pick the "
                "browser where you're logged in (Firefox works best), or load a cookies.txt file.")
    if "private" in low:
        return "This video or post is private."
    if re.search(r"age[- ]restrict|confirm your age|age verification|inappropriate for some users", low):
        return "This video is age-restricted. Add login cookies in Settings to download it."
    if "not available in your country" in low or ("geo" in low and "restrict" in low) \
            or "ip address is blocked" in low or "your ip" in low:
        return "This content isn't available in your country. A proxy (Settings) can help."
    if "unavailable" in low or "removed" in low or "does not exist" in low or "404" in low:
        return "This content is unavailable — it may have been removed or the link is wrong."
    if "drm" in low:
        return "This content is DRM-protected and can't be downloaded."
    if "ffmpeg" in low and ("not found" in low or "not installed" in low):
        return "FFmpeg is missing — it's needed to merge video and audio. See Settings → Engine."
    if "timed out" in low or "connection" in low or "network" in low or "getaddrinfo" in low \
            or "remote end closed" in low or "10054" in low:
        return "Network problem — check your internet connection and try again."
    if "no space" in low or "errno 28" in low:
        return "Your disk is full. Free some space or pick another download folder in Settings."
    if "permission denied" in low or "errno 13" in low:
        return "Can't write to the download folder. Pick another folder in Settings."
    return m[:400] or "Something went wrong."


# ----------------------------------------------------------------------------- yt-dlp side

def _num(v):
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _fmt_size(f: dict, duration) -> float | None:
    size = _num(f.get("filesize")) or _num(f.get("filesize_approx"))
    if not size and duration and f.get("tbr"):
        size = _num(f["tbr"]) * 1000 / 8 * duration
    return size


def _qualities(info: dict, compat: bool) -> tuple[list, list]:
    fmts = info.get("formats") or []
    dur = _num(info.get("duration"))
    audio_only = [f for f in fmts if f.get("vcodec") == "none" and f.get("acodec") not in (None, "none")]
    best_audio = max(audio_only, key=lambda f: (_num(f.get("abr")) or _num(f.get("tbr")) or 0), default=None)
    audio_size = _fmt_size(best_audio, dur) if best_audio else None
    by_h: dict[int, dict] = {}
    for f in fmts:
        if f.get("vcodec") in (None, "none") and not (f.get("height") and f.get("vcodec") is None):
            continue
        h = f.get("height")
        w = f.get("width")
        if not h:
            continue
        h = int(h)
        # use the shorter side for portrait videos so 1080x1920 shows as 1080p
        if w and int(w) < h:
            h = int(w)
        h = _snap(h)
        vc = (f.get("vcodec") or "").lower()
        progressive = f.get("acodec") not in (None, "none")
        size = _fmt_size(f, dur)
        if size and not progressive and audio_size:
            size += audio_size
        # mirror yt-dlp's own choice: compatible codec first, then direct (exact-size) over HLS streams
        exact = 1 if (f.get("filesize") and f.get("protocol", "https") in ("https", "http")) else 0
        score = (1 if (compat and vc.startswith(("avc", "h264"))) else 0, exact, _num(f.get("tbr")) or 0)
        cur = by_h.get(h)
        entry = {"height": h, "fps": int(_num(f.get("fps")) or 0), "hdr": (f.get("dynamic_range") or "SDR") != "SDR",
                 "size": size, "vcodec": vc.split(".")[0], "score": score}
        if cur is None or score > cur["score"]:
            entry["fps"] = max(entry["fps"], cur["fps"] if cur else 0)
            entry["hdr"] = entry["hdr"] or bool(cur and cur["hdr"])
            by_h[h] = entry
        else:
            cur["fps"] = max(cur["fps"], entry["fps"])
            cur["hdr"] = cur["hdr"] or entry["hdr"]
    quals = []
    for h in sorted(by_h, reverse=True):
        e = by_h[h]
        quals.append({"id": str(h), "height": h, "label": f"{h}p", "badge": QUALITY_BADGE.get(h, ""),
                      "fps": e["fps"], "hdr": e["hdr"], "size": e["size"], "vcodec": e["vcodec"]})
    has_audio = bool(audio_only) or any(f.get("acodec") not in (None, "none") for f in fmts)
    audio = []
    if has_audio:
        for aid, label, desc, kbps in AUDIO_CHOICES:
            size = (kbps * 1000 / 8 * dur) if (kbps and dur) else audio_size
            if aid == "wav" and dur:
                size = 44100 * 2 * 2 * dur
            audio.append({"id": aid, "label": label, "desc": desc, "size": size})
    return quals, audio


def _snap(h: int) -> int:
    for std in (4320, 2160, 1440, 1080, 720, 480, 360, 240, 144):
        if abs(h - std) <= max(8, std * 0.04):
            return std
    return h


def _thumbs(info: dict) -> list:
    out, seen = [], set()
    items = list(info.get("thumbnails") or [])
    if info.get("thumbnail") and not any(t.get("url") == info["thumbnail"] for t in items):
        items.append({"url": info["thumbnail"]})
    for t in items:
        u = t.get("url")
        if not u or u in seen:
            continue
        w, h = t.get("width"), t.get("height")
        if not w and "/maxresdefault" in u:
            w, h = 1280, 720
        key = (w, h, u.split("?")[0].rsplit(".", 1)[-1] if not w else "")
        if w and key in seen:
            continue
        seen.add(u)
        seen.add(key)
        ext = "webp" if ".webp" in u or "/vi_webp/" in u else ("png" if ".png" in u else "jpg")
        out.append({"url": u, "width": w, "height": h, "ext": ext})
    # prefer large jpg over equivalent webp; biggest first
    out.sort(key=lambda t: ((t["width"] or 0) * (t["height"] or 0), t["ext"] == "jpg"), reverse=True)
    best, seen_res = [], set()
    for t in out:
        res = (t["width"], t["height"])
        if t["width"] and res in seen_res:
            continue
        seen_res.add(res)
        best.append(t)
    best = best[:8]
    for t in best:
        t["label"] = f"{t['width']}×{t['height']}" if t["width"] else "Original"
    return best


def _subs(info: dict) -> list:
    out = []
    for lang, tracks in (info.get("subtitles") or {}).items():
        if lang == "live_chat":
            continue
        out.append({"lang": lang, "name": (tracks[0].get("name") if tracks else "") or lang, "auto": False})
    have = {s["lang"] for s in out}
    auto = info.get("automatic_captions") or {}
    for lang in ("en", "ar", "fr", "es", "de", "pt", "it", "ru", "tr", "hi", "ja", "ko", "zh-Hans"):
        if lang in auto and lang not in have:
            tracks = auto[lang]
            out.append({"lang": lang, "name": ((tracks[0].get("name") if tracks else "") or lang) + " (auto)",
                        "auto": True})
    return out[:40]


def _entry_url(e: dict) -> str:
    u = e.get("url") or e.get("webpage_url") or ""
    if u and not u.startswith("http"):
        key = (e.get("ie_key") or "").lower()
        if key.startswith("youtube"):
            u = "https://www.youtube.com/watch?v=" + u
    return u


def _ytdlp(url: str, s: dict) -> dict:
    import yt_dlp
    log = _QuietLogger()
    opts = base_opts(s)
    opts.update({"logger": log, "skip_download": True, "extract_flat": "in_playlist", "playlistend": 2000})
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        info = ydl.sanitize_info(info)
    if not info:
        raise AnalyzeError("Nothing found at this link.")
    return info


def _from_ytdlp(info: dict, url: str, s: dict) -> dict:
    site = pretty_site(info.get("extractor_key") or info.get("ie_key") or "", url)
    res = {
        "url": url, "webpage_url": info.get("webpage_url") or url, "site": site,
        "id": info.get("id") or "", "title": info.get("title") or info.get("id") or "Untitled",
        "uploader": info.get("uploader") or info.get("channel") or info.get("uploader_id") or "",
        "duration": _num(info.get("duration")), "thumbnail": info.get("thumbnail") or "",
        "view_count": info.get("view_count"), "upload_date": info.get("upload_date") or "",
        "is_live": bool(info.get("is_live")), "qualities": [], "audio": [], "thumbnails": [],
        "images": [], "subtitles": [], "entries": [], "warnings": [],
    }
    if info.get("_type") in ("playlist", "multi_video"):
        entries = []
        for i, e in enumerate(info.get("entries") or []):
            if not e:
                continue
            eu = _entry_url(e)
            if not eu:
                continue
            th = e.get("thumbnail") or ((e.get("thumbnails") or [{}])[-1].get("url"))
            entries.append({"index": i + 1, "url": eu, "id": e.get("id") or "", "title": e.get("title") or eu,
                            "duration": _num(e.get("duration")), "thumbnail": th or "",
                            "uploader": e.get("uploader") or e.get("channel") or ""})
        res["kind"] = "playlist"
        res["entries"] = entries
        res["playlist_count"] = info.get("playlist_count") or len(entries)
        if not res["thumbnail"]:
            res["thumbnail"] = next((e["thumbnail"] for e in entries if e["thumbnail"]), "")
        res["thumbnails"] = _thumbs(info)
        # a single-entry "playlist" (e.g. one-video post) — analyze the entry directly
        if len(entries) == 1 and entries[0]["url"] != url:
            try:
                inner = _from_ytdlp(_ytdlp(entries[0]["url"], s), entries[0]["url"], s)
                inner["url"] = url
                return inner
            except Exception:
                pass
        return res
    quals, audio = _qualities(info, bool(s.get("compat", True)))
    sized = [f for f in (info.get("formats") or []) if f.get("width") and f.get("height")]
    if sized:
        top = max(sized, key=lambda f: f["width"] * f["height"])
        res["portrait"] = top["width"] < top["height"]
    res["kind"] = "video" if quals else ("audio" if audio else "video")
    res["qualities"] = quals
    res["audio"] = audio
    res["thumbnails"] = _thumbs(info)
    res["subtitles"] = _subs(info)
    if not quals and not audio:
        res["kind"] = "none"
    return res


# ----------------------------------------------------------------------------- gallery-dl side

def _python_cli() -> str:
    exe = sys.executable
    if os.path.basename(exe).lower() == "pythonw.exe":
        alt = os.path.join(os.path.dirname(exe), "python.exe")
        if os.path.isfile(alt):
            return alt
    return exe


def gallery_args(s: dict) -> list:
    args = []
    if s.get("cookies_file") and os.path.isfile(s["cookies_file"]):
        args += ["--cookies", s["cookies_file"]]
    elif s.get("cookies_browser"):
        args += ["--cookies-from-browser", s["cookies_browser"]]
    if s.get("proxy"):
        args += ["--proxy", s["proxy"]]
    return args


def _thumb_of(meta: dict) -> str:
    for k in ("display_url", "thumbnail", "cover", "preview"):
        v = meta.get(k)
        if isinstance(v, str) and v.startswith("http"):
            return v
    vid = meta.get("video")
    if isinstance(vid, dict):
        for k in ("cover", "originCover", "dynamicCover"):
            v = vid.get(k)
            if isinstance(v, str) and v.startswith("http"):
                return v
    return ""


def _uploader(meta: dict) -> str:
    a = meta.get("author") or meta.get("user") or meta.get("owner")
    if isinstance(a, dict):
        return a.get("name") or a.get("username") or a.get("nick") or ""
    return meta.get("username") or (a if isinstance(a, str) else "") or ""


def _gallery(url: str, s: dict, timeout: int = 90) -> list:
    cmd = [_python_cli(), "-m", "gallery_dl", "-j", "--range", "1-500", *gallery_args(s), url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, creationflags=tools.NO_WINDOW)
    except subprocess.TimeoutExpired:
        return []
    try:
        data = json.loads(r.stdout or "[]")
    except json.JSONDecodeError:
        return []
    files = []
    for msg in data if isinstance(data, list) else []:
        if not isinstance(msg, list) or len(msg) < 3 or msg[0] != 3:
            continue
        fu, meta = msg[1], msg[2] if isinstance(msg[2], dict) else {}
        if not isinstance(fu, str) or not fu.startswith("http"):
            continue
        ext = (meta.get("extension") or fu.split("?")[0].rsplit(".", 1)[-1]).lower()
        is_vid = ext in ("mp4", "webm", "mov", "m4v", "m3u8")
        files.append({"index": len(files) + 1, "url": fu, "ext": ext, "video": is_vid,
                      "width": meta.get("width"), "height": meta.get("height"),
                      "title": meta.get("description") or meta.get("desc") or meta.get("content")
                      or meta.get("title") or "",
                      "thumb": _thumb_of(meta),
                      "uploader": _uploader(meta),
                      "category": meta.get("category") or "",
                      "display": meta.get("display_url") or (fu if not is_vid else "")})
    return files


# ----------------------------------------------------------------------------- public

def analyze(raw_url: str) -> dict:
    url = normalize_url(raw_url)
    s = config.load()
    path = urllib.parse.urlparse(url).path.lower()

    # direct image link
    if path.endswith(IMG_EXT):
        name = os.path.basename(urllib.parse.unquote(path)) or "image"
        return {"url": url, "webpage_url": url, "site": site_of(url), "kind": "images", "title": name,
                "uploader": "", "thumbnail": url, "qualities": [], "audio": [], "thumbnails": [],
                "subtitles": [], "entries": [], "warnings": [],
                "images": [{"index": 1, "url": url, "ext": name.rsplit(".", 1)[-1], "video": False,
                            "display": url, "width": None, "height": None, "title": name}],
                "gallery": False}

    want_gallery = any(k in site_of(url) for k in IMAGE_SITES)
    gal_result: dict = {}

    def run_gallery():
        try:
            gal_result["files"] = _gallery(url, s)
        except Exception:
            gal_result["files"] = []

    gt = threading.Thread(target=run_gallery, daemon=True) if want_gallery else None
    if gt:
        gt.start()

    info, err = None, None
    try:
        info = _ytdlp(url, s)
    except Exception as e:  # noqa: BLE001
        err = e

    res = _from_ytdlp(info, url, s) if info else None

    if gt is None and (res is None or res["kind"] == "none"):
        # yt-dlp found no video — maybe it's an image gallery on another site
        gt = threading.Thread(target=run_gallery, daemon=True)
        gt.start()
    if gt:
        gt.join(100)
    files = gal_result.get("files") or []
    images = [f for f in files if not f["video"]]

    if res is None and not files:
        raise AnalyzeError(friendly_error(err) if err else "Nothing downloadable found at this link.")

    if res is None or res["kind"] == "none":
        # yt-dlp couldn't read it — gallery-dl did (image posts, or a site yt-dlp is currently broken on)
        first = files[0]
        vids = [f for f in files if f["video"]]
        res = {"url": url, "webpage_url": url, "site": pretty_host(url), "kind": "images",
               "id": "", "title": (first.get("title") or "").strip().split("\n")[0][:120] or pretty_host(url) + " post",
               "uploader": first.get("uploader") or "", "duration": None,
               "thumbnail": next((f["display"] or f.get("thumb") for f in files if f["display"] or f.get("thumb")), ""),
               "qualities": [], "audio": [], "thumbnails": [], "subtitles": [], "entries": [], "warnings": [],
               "images": files, "gallery": True}
        if len(files) == 1 and vids:
            res["kind"] = "video"
            res["qualities"] = [{"id": "original", "height": 0, "label": "Original", "badge": "Best",
                                 "fps": 0, "hdr": False, "size": None, "vcodec": vids[0]["ext"]}]
            res["images"] = []
        return res
    if images:
        res["images"] = files          # keep videos too so a mixed carousel downloads completely
        res["gallery"] = True
        if res["kind"] == "playlist" and all(not f["video"] for f in files):
            res["kind"] = "images"
    else:
        res.setdefault("images", [])
    if res["kind"] == "images" and not res.get("thumbnail") and images:
        res["thumbnail"] = images[0]["display"]
    if not tools.ffmpeg_dir() and res.get("qualities"):
        res["warnings"].append("FFmpeg not found — HD videos (separate video + audio) can't be merged.")
    return res
