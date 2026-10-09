"""
Download queue.

Every download is a job that survives restarts (SQLite). Partial data lives in a hidden
temp folder next to the destination, so pausing, a crash, a closed laptop lid or a dropped
connection just resumes where it stopped — long videos (hours) are fine. Network failures
are retried automatically with back-off; an embed step that fails never loses the video.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
import subprocess
import threading
import time
import urllib.parse
import uuid

import requests

import app_paths
import config
import extract
import tools

ACTIVE = ("downloading", "processing", "starting", "retrying")
LIVE_FIELDS = ("percent", "speed", "eta", "downloaded", "total", "stage", "stage_label")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/131.0 Safari/537.36")


class Cancelled(Exception):
    pass


class _JobLogger:
    """Keeps yt-dlp quiet in the UI but records the important steps in mediagrab.log."""
    KEEP = ("[Merger]", "[MoveFiles]", "Destination:", "has already been downloaded", "[ExtractAudio]",
            "[EmbedThumbnail]", "[Metadata]", "Downloading 1 format", "Resuming", "Deleting original")

    def __init__(self, jid: str):
        self.jid = jid

    def _w(self, level: str, msg: str):
        try:
            print(f"{time.strftime('%H:%M:%S')} [{self.jid}] {level}: {msg}", flush=True)
        except Exception:
            pass

    def debug(self, msg):
        if any(k in msg for k in self.KEEP):
            self._w("info", msg)

    def info(self, msg):
        self.debug(msg)

    def warning(self, msg):
        self._w("warning", msg)

    def error(self, msg):
        self._w("error", msg)


def _safe(name: str, limit: int = 120) -> str:
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", str(name or "")).strip(" .")
    name = re.sub(r"\s+", " ", name)
    return (name[:limit].rstrip(" .") or "untitled")


def _real_ext(path: str) -> str | None:
    """Detect the actual image/video type from the file's first bytes (sites often serve
    WebP or AVIF from a URL that says .jpg)."""
    try:
        with open(path, "rb") as f:
            head = f.read(32)
    except OSError:
        return None
    if head.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if head.startswith(b"\x89PNG"):
        return ".png"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return ".webp"
    if head.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if head[4:8] == b"ftyp":
        brand = head[8:12]
        if brand in (b"avif", b"avis"):
            return ".avif"
        if brand in (b"heic", b"heix", b"mif1"):
            return ".heic"
        return ".mp4"
    if head.startswith(b"\x1aE\xdf\xa3"):
        return ".webm"
    return None


def _unique(path: str) -> str:
    if not os.path.exists(path):
        return path
    root, ext = os.path.splitext(path)
    i = 1
    while os.path.exists(f"{root} ({i}){ext}"):
        i += 1
    return f"{root} ({i}){ext}"


class Manager:
    def __init__(self):
        self.jobs: dict[str, dict] = {}
        self.lock = threading.RLock()
        self.wake = threading.Event()
        self.procs: dict[str, subprocess.Popen] = {}
        self.db_path = os.path.join(app_paths.data_dir(), "mediagrab.db")
        self._db_lock = threading.Lock()
        self._init_db()
        self._load()
        threading.Thread(target=self._dispatcher, daemon=True, name="dispatcher").start()

    # ------------------------------------------------------------------ storage
    def _conn(self):
        c = sqlite3.connect(self.db_path, timeout=30)
        c.execute("PRAGMA journal_mode=WAL")
        return c

    def _init_db(self):
        with self._db_lock, self._conn() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY, created REAL, updated REAL, data TEXT)""")

    def _persist(self, job: dict):
        row = {k: v for k, v in job.items() if k not in LIVE_FIELDS and not k.startswith("_")}
        with self._db_lock, self._conn() as c:
            c.execute("INSERT OR REPLACE INTO jobs(id, created, updated, data) VALUES (?,?,?,?)",
                      (job["id"], job["created"], time.time(), json.dumps(row)))

    def _delete_row(self, jid: str):
        with self._db_lock, self._conn() as c:
            c.execute("DELETE FROM jobs WHERE id=?", (jid,))

    def _load(self):
        with self._db_lock, self._conn() as c:
            rows = c.execute("SELECT data FROM jobs ORDER BY created").fetchall()
        for (data,) in rows:
            try:
                job = json.loads(data)
            except json.JSONDecodeError:
                continue
            # anything interrupted by a restart picks up where it left off
            if job.get("status") in ACTIVE:
                job["status"] = "queued"
            job.update({k: None for k in LIVE_FIELDS})
            self.jobs[job["id"]] = job

    # ------------------------------------------------------------------ public api
    def add(self, spec: dict) -> dict:
        jid = time.strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:6]
        mode = spec.get("mode") or "video"
        job = {
            "id": jid, "created": time.time(), "status": "queued", "spec": spec, "mode": mode,
            "title": (spec.get("title") or spec.get("url") or "Download")[:300],
            "thumbnail": spec.get("thumbnail") or "", "site": spec.get("site") or extract.pretty_host(spec.get("url", "")),
            "label": spec.get("label") or "", "filepath": "", "files": [], "size": None, "error": "",
            "attempts": 0, "note": "", "finished": None,
        }
        job.update({k: None for k in LIVE_FIELDS})
        with self.lock:
            self.jobs[jid] = job
        self._persist(job)
        self.wake.set()
        return self.public(job)

    def public(self, job: dict) -> dict:
        return {k: v for k, v in job.items() if not k.startswith("_") and k != "spec"} | {
            "url": job["spec"].get("url", ""), "mode": job.get("mode")}

    def list(self) -> list:
        with self.lock:
            jobs = sorted(self.jobs.values(), key=lambda j: j["created"], reverse=True)
            return [self.public(j) for j in jobs]

    def get(self, jid: str) -> dict | None:
        with self.lock:
            return self.jobs.get(jid)

    def control(self, jid: str, action: str) -> dict | None:
        with self.lock:
            job = self.jobs.get(jid)
            if not job:
                return None
            st = job["status"]
            if action == "pause" and st in ACTIVE + ("queued",):
                if st == "queued":
                    job["status"] = "paused"
                else:
                    job["_stop"] = "paused"
                    self._kill(jid)
            elif action == "resume" and st in ("paused", "error", "cancelled"):
                job.update(status="queued", error="", attempts=0, note="")
                job.pop("_stop", None)
            elif action == "retry" and st in ("error", "cancelled", "done"):
                job.update(status="queued", error="", attempts=0, note="", filepath="", files=[], size=None)
                job.pop("_stop", None)
            elif action == "cancel" and st in ACTIVE + ("queued", "paused"):
                if st in ("queued", "paused"):
                    job["status"] = "cancelled"
                    self._cleanup_tmp(job)
                else:
                    job["_stop"] = "cancelled"
                    self._kill(jid)
            elif action == "remove":
                if st in ACTIVE:
                    job["_stop"] = "removed"
                    self._kill(jid)
                else:
                    self._cleanup_tmp(job)
                    self.jobs.pop(jid, None)
                    self._delete_row(jid)
                    return {"removed": True}
            self._persist(job)
        self.wake.set()
        return self.public(job)

    def clear(self, which: str = "finished") -> int:
        n = 0
        with self.lock:
            for jid, job in list(self.jobs.items()):
                st = job["status"]
                if (which == "finished" and st == "done") or (which == "failed" and st in ("error", "cancelled")) \
                        or (which == "all" and st not in ACTIVE):
                    self._cleanup_tmp(job)
                    self.jobs.pop(jid, None)
                    self._delete_row(jid)
                    n += 1
        return n

    def pause_all(self):
        for j in self.list():
            if j["status"] in ACTIVE + ("queued",):
                self.control(j["id"], "pause")

    def resume_all(self):
        for j in self.list():
            if j["status"] == "paused":
                self.control(j["id"], "resume")

    # ------------------------------------------------------------------ internals
    def _kill(self, jid: str):
        p = self.procs.get(jid)
        if p and p.poll() is None:
            try:
                p.kill()
            except Exception:
                pass

    def _stop_flag(self, job: dict):
        if job.get("_stop"):
            raise Cancelled(job["_stop"])

    def _set(self, job: dict, persist: bool = False, **kw):
        with self.lock:
            job.update(kw)
        if persist:
            self._persist(job)

    def _dispatcher(self):
        while True:
            self.wake.wait(1.0)
            self.wake.clear()
            try:
                limit = config.load()["concurrency"]
                with self.lock:
                    running = sum(1 for j in self.jobs.values() if j["status"] in ACTIVE)
                    queued = sorted((j for j in self.jobs.values() if j["status"] == "queued"),
                                    key=lambda j: j["created"])
                    for job in queued[: max(0, limit - running)]:
                        job["status"] = "starting"
                        job.pop("_stop", None)
                        threading.Thread(target=self._run, args=(job,), daemon=True).start()
            except Exception:
                pass

    # paths ------------------------------------------------------------
    def _dirs(self, job: dict) -> tuple[str, str]:
        s = config.load()
        base = s["download_dir"] or app_paths.default_download_dir()
        out = base
        if s.get("subfolder_by_site") and job.get("site"):
            out = os.path.join(out, _safe(job["site"], 40))
        if s.get("playlist_subfolder") and job["spec"].get("folder"):
            out = os.path.join(out, _safe(job["spec"]["folder"], 80))
        tmp = os.path.join(base, ".mediagrab-temp", job["id"])
        os.makedirs(out, exist_ok=True)
        os.makedirs(tmp, exist_ok=True)
        if os.name == "nt":
            try:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(os.path.join(base, ".mediagrab-temp"), 0x02)
            except Exception:
                pass
        return out, tmp

    def _cleanup_tmp(self, job: dict):
        try:
            base = config.load()["download_dir"]
            shutil.rmtree(os.path.join(base, ".mediagrab-temp", job["id"]), ignore_errors=True)
        except Exception:
            pass

    # run ---------------------------------------------------------------
    def _run(self, job: dict):
        s = config.load()
        self._set(job, persist=True, status="downloading", error="", note="", stage_label="Starting…",
                  percent=None, speed=None, eta=None, downloaded=None, total=None)
        try:
            out, tmp = self._dirs(job)
            free = shutil.disk_usage(out).free
            if free < 300 * 1024 * 1024:
                raise RuntimeError("errno 28: no space left on the download drive")
            mode = job["mode"]
            if mode in ("video", "audio"):
                try:
                    self._run_ytdlp(job, out, tmp, s)
                except Cancelled:
                    raise
                except Exception as first:  # noqa: BLE001
                    # yt-dlp can't handle it right now — gallery-dl often still can (TikTok, image posts)
                    if mode != "video" or job.get("_stop") or extract.friendly_error(str(first)).startswith(
                            ("Network problem", "Your disk", "Can't write")):
                        raise
                    try:
                        self._set(job, note="", stage_label="Trying another method…")
                        self._run_gallery(job, out, tmp, s)
                    except Cancelled:
                        raise
                    except Exception:
                        raise first
            elif mode == "gallery":
                self._run_gallery(job, out, tmp, s)
            else:
                self._run_files(job, out, tmp)
            self._cleanup_tmp(job)
            self._set(job, persist=True, status="done", finished=time.time(), percent=100, stage_label="Done",
                      speed=None, eta=None)
        except Cancelled as c:
            job["_stop"] = job.get("_stop") or str(c)
            self._run_after_stop(job)
        except Exception as e:  # noqa: BLE001
            msg = extract.friendly_error(str(e))
            if job.get("_stop"):
                return self._run_after_stop(job)
            retries = int(s.get("auto_retry", 3))
            transient = msg.startswith("Network problem") or "http error 5" in str(e).lower() \
                or "403" in str(e) or "timed out" in str(e).lower()
            if transient and job["attempts"] < retries:
                job["attempts"] += 1
                wait = min(60, 5 * 2 ** (job["attempts"] - 1))
                for left in range(wait, 0, -1):
                    if job.get("_stop"):
                        return self._run_after_stop(job)
                    self._set(job, status="retrying", stage_label=f"Connection lost — retrying in {left}s "
                                                                  f"({job['attempts']}/{retries})", speed=None)
                    time.sleep(1)
                return self._run(job)
            self._set(job, persist=True, status="error", error=msg, speed=None, eta=None, stage_label="Failed")
        finally:
            self.procs.pop(job["id"], None)
            self.wake.set()

    def _run_after_stop(self, job: dict):
        why = job.get("_stop")
        if why == "removed":
            self._cleanup_tmp(job)
            with self.lock:
                self.jobs.pop(job["id"], None)
            self._delete_row(job["id"])
        elif why == "cancelled":
            self._cleanup_tmp(job)
            self._set(job, persist=True, status="cancelled", speed=None, eta=None, stage_label="Cancelled")
        else:
            self._set(job, persist=True, status="paused", speed=None, eta=None, stage_label="Paused")

    # yt-dlp ------------------------------------------------------------
    def _ytdlp_opts(self, job: dict, out: str, tmp: str, s: dict, embeds: bool = True) -> dict:
        import yt_dlp
        from yt_dlp.utils import download_range_func, parse_bytes
        spec = job["spec"]
        o = extract.base_opts(s)
        o.update({
            "paths": {"home": out, "temp": tmp},
            "outtmpl": {"default": self._template(job, s)},
            "continuedl": True,
            "overwrites": False,
            "concurrent_fragment_downloads": s.get("fragments", 4),
            "http_chunk_size": 10 * 1024 * 1024,
            "noplaylist": True,
            "progress_hooks": [lambda d: self._hook(job, d)],
            "postprocessor_hooks": [lambda d: self._pp_hook(job, d)],
            "logger": _JobLogger(job["id"]),
        })
        if s.get("rate_limit"):
            try:
                o["ratelimit"] = parse_bytes(s["rate_limit"])
            except Exception:
                pass
        pps: list = []
        mode = job["mode"]
        if mode == "audio":
            a = spec.get("audio") or "mp3-320"
            codec, _, q = a.partition("-")
            o["format"] = "bestaudio/best"
            o["format_sort"] = ["acodec:aac"] if codec == "m4a" else (["acodec:opus"] if codec == "opus" else [])
            pps.append({"key": "FFmpegExtractAudio", "preferredcodec": codec,
                        "preferredquality": q or "0", "nopostoverwrites": False})
        else:
            q = str(spec.get("quality") or "best")
            sort = []
            if q.isdigit():
                sort.append(f"res:{q}")
            if s.get("compat", True):
                sort += ["vcodec:h264", "acodec:aac", "ext:mp4:m4a"]
            o["format"] = "bestvideo*+bestaudio/best/bestvideo*"
            if q.isdigit() and spec.get("portrait") is not None:
                # the chosen quality is a hard cap (a sort preference alone can be overridden by
                # the site's own format ranking); cap the short side: height, or width for portrait
                dim = "width" if spec["portrait"] else "height"
                o["format"] = (f"bestvideo*[{dim}<={q}]+bestaudio/best[{dim}<={q}]/bestvideo*[{dim}<={q}]/"
                               + o["format"])
            o["format_sort"] = sort
            cont = spec.get("container") if spec.get("container") in ("mp4", "mkv") else s.get("container")
            o["merge_output_format"] = cont or "mp4"
        subs = spec.get("subs") or []
        if subs and mode == "video":
            o.update({"writesubtitles": True, "writeautomaticsub": True, "subtitleslangs": subs,
                      "subtitlesformat": "srt/vtt/best"})
            pps.insert(0, {"key": "FFmpegSubtitlesConvertor", "format": "srt", "when": "before_dl"})
            if s.get("embed_subs"):
                pps.append({"key": "FFmpegEmbedSubtitle", "already_have_subtitle": False})
        trim = spec.get("trim") or {}
        if trim.get("start") is not None or trim.get("end") is not None:
            start = float(trim.get("start") or 0)
            end = float(trim["end"]) if trim.get("end") not in (None, "") else float("inf")
            o["download_ranges"] = download_range_func(None, [(start, end)])
            o["force_keyframes_at_cuts"] = True
        if embeds and s.get("embed_metadata", True):
            pps.append({"key": "FFmpegMetadata", "add_metadata": True, "add_chapters": True})
        can_cover = mode == "video" or (spec.get("audio") or "mp3").split("-")[0] in ("mp3", "m4a", "opus")
        if embeds and s.get("embed_thumbnail", True) and can_cover and not trim:
            o["writethumbnail"] = True
            pps.insert(0, {"key": "FFmpegThumbnailsConvertor", "format": "jpg", "when": "before_dl"})
            pps.append({"key": "EmbedThumbnail", "already_have_thumbnail": False})
        o["postprocessors"] = pps
        _ = yt_dlp  # imported for side effects / availability check
        return o

    @staticmethod
    def _template(job: dict, s: dict) -> str:
        """Different qualities / clips of the same video must never share a file name —
        otherwise yt-dlp treats the second one as 'already downloaded'."""
        tmpl = s.get("filename") or config.DEFAULTS["filename"]
        spec = job["spec"]
        tag = ""
        if job["mode"] == "video":
            tag = "%(height& {}p|)s"
        elif job["mode"] == "audio" and "-" in (spec.get("audio") or ""):
            tag = " " + spec["audio"].split("-", 1)[1] + "k"
        trim = spec.get("trim") or {}
        if trim.get("start") is not None or trim.get("end") is not None:
            a = int(float(trim.get("start") or 0))
            b = trim.get("end")
            tag += f" clip {a // 60}m{a % 60:02d}s-" + (f"{int(float(b)) // 60}m{int(float(b)) % 60:02d}s"
                                                       if b not in (None, "") else "end")
        if tag and tmpl.endswith(".%(ext)s"):
            tmpl = tmpl[: -len(".%(ext)s")] + tag + ".%(ext)s"
        return tmpl

    def _run_ytdlp(self, job: dict, out: str, tmp: str, s: dict):
        import yt_dlp
        from yt_dlp.utils import DownloadCancelled, PostProcessingError
        url = job["spec"]["url"]
        embeds = not job.get("_noembed")
        for attempt in (1, 2):
            job["_streams"] = []
            opts = self._ytdlp_opts(job, out, tmp, s, embeds=embeds)
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    info = ydl.sanitize_info(info) if info else {}
                break
            except DownloadCancelled:
                raise Cancelled(job.get("_stop") or "paused")
            except Cancelled:
                raise
            except (PostProcessingError, yt_dlp.utils.DownloadError) as e:
                if job.get("_stop"):
                    raise Cancelled(job["_stop"])
                pp_fail = isinstance(e, PostProcessingError) or "postprocessing" in str(e).lower() \
                    or "embed" in str(e).lower() or "thumbnail" in str(e).lower()
                if embeds and pp_fail and attempt == 1:
                    embeds = False           # the video itself is fine; skip the cover/metadata step
                    job["_noembed"] = True
                    self._set(job, note="Cover/metadata couldn't be embedded — saved without it.")
                    continue
                raise
        files = []
        # a playlist link (e.g. from batch mode) downloads every entry
        for item in [info, *[e for e in (info.get("entries") or []) if e]]:
            for rd in (item.get("requested_downloads") or []):
                fp = rd.get("filepath") or rd.get("_filename")
                if fp and os.path.isfile(fp) and fp not in files:
                    files.append(fp)
        if not files and info.get("filepath") and os.path.isfile(info["filepath"]):
            files.append(info["filepath"])
        if not files:
            # already downloaded earlier / unusual extractor — pick the newest file in the folder
            cands = [os.path.join(out, f) for f in os.listdir(out)]
            cands = [c for c in cands if os.path.isfile(c) and os.path.getmtime(c) >= job["created"] - 5]
            if cands:
                files.append(max(cands, key=os.path.getmtime))
        if not files:
            raise RuntimeError("Download finished but no file was produced.")
        # safety net: a video+audio download must end as ONE merged file, never a ".f137.mp4" piece
        if job["mode"] == "video" and len(info.get("requested_formats") or []) > 1:
            pieces = [f for f in files if re.search(r"\.f[0-9A-Za-z_-]+\.[A-Za-z0-9]+$", f)]
            if pieces:
                for f in pieces:
                    stem = re.sub(r"\.f[0-9A-Za-z_-]+\.[A-Za-z0-9]+$", "", f)
                    for extra in (f, stem + ".jpg", stem + ".webp", stem + ".png"):
                        try:
                            os.remove(extra)
                        except OSError:
                            pass
                if job.get("_remerged"):
                    raise RuntimeError("Couldn't merge the video and audio. Try MKV format or another quality.")
                job["_remerged"] = True
                print(f"[{job['id']}] unmerged result {pieces} - downloading again cleanly", flush=True)
                shutil.rmtree(tmp, ignore_errors=True)
                os.makedirs(tmp, exist_ok=True)
                self._set(job, note="", stage_label="Re-downloading to fix the file…", percent=0)
                return self._run_ytdlp(job, out, tmp, s)
        size = sum(os.path.getsize(f) for f in files)
        if os.path.getmtime(files[0]) < job["created"] - 2:
            self._set(job, note="Already in your downloads folder — kept the existing file.")
        if not job["title"] or job["title"] == job["spec"]["url"]:
            job["title"] = info.get("title") or job["title"]
        if not job["thumbnail"]:
            job["thumbnail"] = info.get("thumbnail") or ""
        self._set(job, filepath=files[0], files=files, size=size)

    def _hook(self, job: dict, d: dict):
        if job.get("_stop"):
            from yt_dlp.utils import DownloadCancelled
            raise DownloadCancelled()
        st = d.get("status")
        info = d.get("info_dict") or {}
        if info.get("title") and job["title"] in ("", job["spec"].get("url")):
            job["title"] = info["title"][:300]
            job["thumbnail"] = job["thumbnail"] or info.get("thumbnail") or ""
            self._persist(job)
        fname = d.get("filename") or d.get("tmpfilename") or ""
        streams = job.setdefault("_streams", [])
        if fname and fname not in streams and st in ("downloading", "finished"):
            streams.append(fname)
        n_req = len(info.get("requested_formats") or []) or 1
        idx = max(1, streams.index(fname) + 1 if fname in streams else len(streams))
        vcodec = info.get("vcodec")
        what = "audio" if vcodec in (None, "none") and job["mode"] == "video" and n_req > 1 else (
            "video" if job["mode"] == "video" else "audio")
        if st == "downloading":
            done = d.get("downloaded_bytes") or 0
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            pct = (done / total * 100) if total else None
            if pct is None and d.get("fragment_count"):
                pct = (d.get("fragment_index") or 0) / d["fragment_count"] * 100
            label = f"Downloading {what}" + (f" ({idx}/{n_req})" if n_req > 1 else "")
            self._set(job, status="downloading", percent=min(99.9, pct) if pct is not None else None,
                      speed=d.get("speed"), eta=d.get("eta"), downloaded=done, total=total or None,
                      stage_label=label)
        elif st == "finished":
            self._set(job, percent=100 if idx >= n_req else job.get("percent"), speed=None, eta=None)

    def _pp_hook(self, job: dict, d: dict):
        if job.get("_stop"):
            from yt_dlp.utils import DownloadCancelled
            raise DownloadCancelled()
        if d.get("status") != "started":
            return
        names = {"Merger": "Merging video + audio", "FFmpegMerger": "Merging video + audio",
                 "ExtractAudio": "Converting audio", "FFmpegExtractAudio": "Converting audio",
                 "EmbedThumbnail": "Adding cover image", "FFmpegMetadata": "Writing info & chapters",
                 "Metadata": "Writing info & chapters", "FFmpegEmbedSubtitle": "Embedding subtitles",
                 "EmbedSubtitle": "Embedding subtitles", "FFmpegSubtitlesConvertor": "Preparing subtitles",
                 "SubtitlesConvertor": "Preparing subtitles", "MoveFiles": "Saving",
                 "FFmpegThumbnailsConvertor": "Preparing cover", "ThumbnailsConvertor": "Preparing cover",
                 "FFmpegFixupM3u8": "Fixing stream", "FFmpegFixupM4a": "Fixing audio",
                 "FFmpegFixupStretched": "Fixing aspect", "FFmpegFixupDuplicateMoov": "Fixing file",
                 "FFmpegFixupTimestamp": "Fixing timestamps", "FFmpegCopyStream": "Saving"}
        pp = d.get("postprocessor") or ""
        if pp in ("FFmpegThumbnailsConvertor", "ThumbnailsConvertor", "FFmpegSubtitlesConvertor",
                  "SubtitlesConvertor") and not job.get("_streams"):
            # these run before the download starts — don't flash the bar to 100 %
            self._set(job, stage_label=names.get(pp, "Preparing…"))
            return
        self._set(job, status="processing", percent=100, speed=None, eta=None,
                  stage_label=names.get(pp, "Finishing…"))

    # gallery-dl ----------------------------------------------------------
    def _run_gallery(self, job: dict, out: str, tmp: str, s: dict):
        spec = job["spec"]
        sel = spec.get("indices") or []
        cmd = [extract._python_cli(), "-m", "gallery_dl", "-D", tmp, "--retries", "8",
               "--http-timeout", "30", *extract.gallery_args(s)]
        if sel:
            cmd += ["--range", ",".join(str(int(i)) for i in sel)]
        cmd.append(spec["url"])
        total = len(sel) or spec.get("count") or 0
        self._set(job, stage_label="Downloading images", percent=0, total=None)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
                             errors="replace", creationflags=tools.NO_WINDOW)
        self.procs[job["id"]] = p
        got = 0
        for line in p.stdout:
            if job.get("_stop"):
                self._kill(job["id"])
                raise Cancelled(job["_stop"])
            if line.strip():
                got += 1
                self._set(job, percent=(got / total * 100) if total else None,
                          stage_label=f"Downloading images ({got}/{total or '?'})")
        p.wait()
        if job.get("_stop"):
            raise Cancelled(job["_stop"])
        files = []
        for root, _d, names in os.walk(tmp):
            for n in sorted(names):
                if n.endswith((".part", ".json")):
                    continue
                src = os.path.join(root, n)
                dst = _unique(os.path.join(out, n))
                shutil.move(src, dst)
                files.append(dst)
        if not files:
            err = (p.stderr.read() if p.stderr else "") or "No images were downloaded."
            raise RuntimeError(err.strip().splitlines()[-1] if err.strip() else "No images were downloaded.")
        self._set(job, filepath=files[0], files=files, size=sum(os.path.getsize(f) for f in files))

    # direct files (thumbnails, image links) ------------------------------
    def _run_files(self, job: dict, out: str, tmp: str):
        spec = job["spec"]
        items = spec.get("files") or []
        if not items:
            raise RuntimeError("Nothing selected.")
        files, total_done = [], 0
        sess = requests.Session()
        sess.headers.update({"User-Agent": UA})
        ref = spec.get("referer") or spec.get("url")
        if ref:
            sess.headers["Referer"] = ref
        for i, it in enumerate(items, 1):
            self._stop_flag(job)
            url = it["url"]
            if not extract.is_public_host(url):
                raise RuntimeError("Blocked a link to a private network address.")
            name = _safe(it.get("name") or os.path.basename(urllib.parse.urlparse(url).path) or f"file-{i}")
            part = os.path.join(tmp, f"{i}.part")
            have = os.path.getsize(part) if os.path.exists(part) else 0
            headers = {"Range": f"bytes={have}-"} if have else {}
            for net_try in range(4):
                try:
                    with sess.get(url, stream=True, timeout=30, headers=headers) as r:
                        if r.status_code == 416:
                            break
                        r.raise_for_status()
                        mode = "ab" if have and r.status_code == 206 else "wb"
                        if mode == "wb":
                            have = 0
                        clen = int(r.headers.get("Content-Length") or 0)
                        ctype = (r.headers.get("Content-Type") or "").split(";")[0]
                        if "." not in name[-6:]:
                            ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
                                   "image/gif": ".gif", "image/avif": ".avif", "video/mp4": ".mp4"}.get(ctype, "")
                            name += ext
                        with open(part, mode) as f:
                            for chunk in r.iter_content(256 * 1024):
                                self._stop_flag(job)
                                f.write(chunk)
                                have += len(chunk)
                                self._set(job, stage_label=f"Downloading ({i}/{len(items)})",
                                          percent=((i - 1) + (have / (clen + (have if mode == 'ab' else 0))
                                                              if clen else 0.5)) / len(items) * 100,
                                          downloaded=total_done + have)
                    break
                except Cancelled:
                    raise
                except requests.RequestException:
                    if net_try == 3:
                        raise
                    time.sleep(2 * (net_try + 1))
                    have = os.path.getsize(part) if os.path.exists(part) else 0
                    headers = {"Range": f"bytes={have}-"} if have else {}
            real = _real_ext(part)
            root_name, ext = os.path.splitext(name)
            if real and ext.lower() != real and not (real == ".jpg" and ext.lower() in (".jpeg", ".jfif")):
                name = root_name + real
            dst = _unique(os.path.join(out, name))
            shutil.move(part, dst)
            total_done += os.path.getsize(dst)
            files.append(dst)
        self._set(job, filepath=files[0], files=files, size=total_done)


MANAGER: Manager | None = None


def manager() -> Manager:
    global MANAGER
    if MANAGER is None:
        MANAGER = Manager()
    return MANAGER
