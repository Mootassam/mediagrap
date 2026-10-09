#!/usr/bin/env python3
"""
MediaGrab — download videos, audio, thumbnails and images from YouTube, TikTok,
Instagram, X, Facebook, Vimeo, Reddit and 1800+ other sites. Runs on your PC.

    python server.py   ->   http://127.0.0.1:5190
"""

from __future__ import annotations

import collections
import os
import subprocess
import sys
import threading
import time

from flask import Flask, Response, abort, jsonify, request, send_from_directory

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import app_paths    # noqa: E402
import config       # noqa: E402
import downloader   # noqa: E402
import extract      # noqa: E402
import tools        # noqa: E402

VERSION = "1.0.0"
APP_ID = "mediagrab"
DEFAULT_PORT = 5190
app = Flask(__name__, static_folder=app_paths.static_dir())
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024


def ok(**kw):
    return jsonify({"ok": True, **kw})


def fail(msg, code=400):
    return jsonify({"ok": False, "error": msg}), code


# ------------------------------------------------------------------ pages
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/favicon.ico")
def favicon():
    p = os.path.join(app_paths.resource_dir(), "mediagrab.ico")
    if os.path.isfile(p):
        return send_from_directory(app_paths.resource_dir(), "mediagrab.ico", mimetype="image/x-icon")
    abort(404)


@app.after_request
def no_cache(resp):
    if request.path == "/" or request.path.startswith("/static/"):
        resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/api/ping")
def ping():
    return jsonify({"app": APP_ID, "version": VERSION})


@app.route("/api/state")
def state():
    return ok(version=VERSION, settings=config.load(), tools=tools.status(),
              installed=app_paths.is_installed())


# ------------------------------------------------------------------ analyze
_ANALYZE_CACHE: "collections.OrderedDict[str, tuple[float, dict]]" = collections.OrderedDict()
_ACACHE_LOCK = threading.Lock()


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    url = ((request.get_json(silent=True) or {}).get("url") or "").strip()
    fresh = bool((request.get_json(silent=True) or {}).get("fresh"))
    try:
        url = extract.normalize_url(url)
    except extract.AnalyzeError as e:
        return fail(str(e))
    with _ACACHE_LOCK:
        hit = _ANALYZE_CACHE.get(url)
        if hit and not fresh and time.time() - hit[0] < 600:
            return ok(result=hit[1])
    try:
        res = extract.analyze(url)
    except extract.AnalyzeError as e:
        return fail(str(e), 422)
    except Exception as e:  # noqa: BLE001
        return fail(extract.friendly_error(str(e)), 422)
    with _ACACHE_LOCK:
        _ANALYZE_CACHE[url] = (time.time(), res)
        while len(_ANALYZE_CACHE) > 50:
            _ANALYZE_CACHE.popitem(last=False)
    return ok(result=res)


# ------------------------------------------------------------------ downloads
@app.route("/api/download", methods=["POST"])
def api_download():
    b = request.get_json(silent=True) or {}
    specs = b.get("specs") or ([b["spec"]] if b.get("spec") else [])
    if not specs:
        return fail("Nothing to download.")
    jobs = []
    for spec in specs[:2000]:
        try:
            spec["url"] = extract.normalize_url(spec.get("url", ""))
        except extract.AnalyzeError as e:
            return fail(str(e))
        if spec.get("mode") not in ("video", "audio", "files", "gallery"):
            spec["mode"] = "video"
        jobs.append(downloader.manager().add(spec))
    return ok(jobs=jobs)


@app.route("/api/jobs")
def api_jobs():
    return ok(jobs=downloader.manager().list())


@app.route("/api/jobs/<jid>/<action>", methods=["POST"])
def api_job_action(jid, action):
    if action not in ("pause", "resume", "cancel", "retry", "remove"):
        return fail("Unknown action.")
    r = downloader.manager().control(jid, action)
    return ok(job=r) if r is not None else fail("Not found.", 404)


@app.route("/api/jobs/bulk", methods=["POST"])
def api_jobs_bulk():
    action = (request.get_json(silent=True) or {}).get("action")
    m = downloader.manager()
    if action == "pause-all":
        m.pause_all()
    elif action == "resume-all":
        m.resume_all()
    elif action in ("clear-finished", "clear-failed", "clear-all"):
        return ok(removed=m.clear(action.split("-", 1)[1]))
    else:
        return fail("Unknown action.")
    return ok()


@app.route("/api/open", methods=["POST"])
def api_open():
    b = request.get_json(silent=True) or {}
    what = b.get("what") or "folder"
    path = ""
    if b.get("id"):
        job = downloader.manager().get(b["id"])
        if not job:
            return fail("Not found.", 404)
        path = job.get("filepath") or ""
        if not path or not os.path.exists(path):
            return fail("The file was moved or deleted.", 404)
    if what == "downloads" or not path:
        d = config.load()["download_dir"]
        os.makedirs(d, exist_ok=True)
        os.startfile(d)  # noqa: S606
    elif what == "file":
        os.startfile(path)  # noqa: S606
    else:
        subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
    return ok()


# ------------------------------------------------------------------ thumbnails proxy
_THUMBS: "collections.OrderedDict[str, tuple[bytes, str]]" = collections.OrderedDict()
_THUMB_LOCK = threading.Lock()


@app.route("/api/thumb")
def api_thumb():
    """Show remote thumbnails without hot-link / CORS problems (Instagram & TikTok CDNs)."""
    import requests
    u = request.args.get("u", "")
    if not u.startswith(("http://", "https://")):
        abort(400)
    with _THUMB_LOCK:
        if u in _THUMBS:
            _THUMBS.move_to_end(u)
            data, ctype = _THUMBS[u]
            return Response(data, mimetype=ctype, headers={"Cache-Control": "max-age=3600"})
    if not extract.is_public_host(u):
        abort(403)
    try:
        r = requests.get(u, timeout=15, stream=True, headers={"User-Agent": downloader.UA})
        r.raise_for_status()
        ctype = r.headers.get("Content-Type", "image/jpeg").split(";")[0]
        if not ctype.startswith("image/"):
            abort(415)
        data = b""
        for chunk in r.iter_content(64 * 1024):
            data += chunk
            if len(data) > 12 * 1024 * 1024:
                abort(413)
    except Exception:
        abort(502)
    with _THUMB_LOCK:
        _THUMBS[u] = (data, ctype)
        total = sum(len(v[0]) for v in _THUMBS.values())
        while total > 80 * 1024 * 1024 and _THUMBS:
            _, (d, _c) = _THUMBS.popitem(last=False)
            total -= len(d)
    return Response(data, mimetype=ctype, headers={"Cache-Control": "max-age=3600"})


# ------------------------------------------------------------------ settings
@app.route("/api/settings", methods=["GET", "POST"])
def api_settings():
    if request.method == "POST":
        patch = request.get_json(silent=True) or {}
        if "download_dir" in patch and patch["download_dir"]:
            try:
                os.makedirs(patch["download_dir"], exist_ok=True)
            except OSError:
                return fail("Can't create or use that folder.")
        return ok(settings=config.save(patch))
    return ok(settings=config.load())


@app.route("/api/pick-folder", methods=["POST"])
def api_pick_folder():
    """Native Windows folder picker (works without tkinter in the embedded runtime)."""
    cur = config.load()["download_dir"].replace("'", "''")
    ps = ("Add-Type -AssemblyName System.Windows.Forms;"
          "$f = New-Object System.Windows.Forms.FolderBrowserDialog;"
          "$f.Description = 'Choose where MediaGrab saves downloads';"
          f"$f.SelectedPath = '{cur}'; $f.ShowNewFolderButton = $true;"
          "$o = New-Object System.Windows.Forms.Form; $o.TopMost = $true;"
          "if ($f.ShowDialog($o) -eq 'OK') { [Console]::OutputEncoding=[Text.Encoding]::UTF8; $f.SelectedPath }")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-STA", "-Command", ps], capture_output=True,
                           text=True, encoding="utf-8", timeout=600, creationflags=tools.NO_WINDOW)
    except Exception as e:  # noqa: BLE001
        return fail(str(e))
    path = (r.stdout or "").strip()
    if not path:
        return ok(settings=config.load(), picked=False)
    return ok(settings=config.save({"download_dir": path}), picked=True)


@app.route("/api/cookies", methods=["POST", "DELETE"])
def api_cookies():
    dst = os.path.join(app_paths.data_dir(), "cookies.txt")
    if request.method == "DELETE":
        try:
            os.remove(dst)
        except OSError:
            pass
        return ok(settings=config.save({"cookies_file": ""}))
    f = request.files.get("file")
    if not f:
        return fail("Choose a cookies.txt file.")
    data = f.read()
    text = data.decode("utf-8", "replace")
    if "\t" not in text or ("# Netscape" not in text and "# HTTP Cookie File" not in text
                             and text.count("\t") < 6):
        return fail("That isn't a Netscape-format cookies.txt file.")
    with open(dst, "wb") as out:
        out.write(data)
    return ok(settings=config.save({"cookies_file": dst, "cookies_browser": ""}))


_UPDATE = {"running": False, "ok": None, "log": ""}


@app.route("/api/update-engines", methods=["GET", "POST"])
def api_update_engines():
    if request.method == "POST" and not _UPDATE["running"]:
        def run():
            _UPDATE.update(running=True, ok=None, log="")
            good, log = tools.update_engines()
            _UPDATE.update(running=False, ok=good, log=log)
        threading.Thread(target=run, daemon=True).start()
        _UPDATE["running"] = True
    return ok(update=dict(_UPDATE), tools=tools.status())


_FFMPEG = {"running": False, "ok": None, "log": ""}


@app.route("/api/install-ffmpeg", methods=["GET", "POST"])
def api_install_ffmpeg():
    if request.method == "POST" and not _FFMPEG["running"] and not tools.ffmpeg_dir():
        def run():
            _FFMPEG.update(running=True, ok=None, log="")
            good, log = tools.install_ffmpeg()
            _FFMPEG.update(running=False, ok=good, log=log)
        threading.Thread(target=run, daemon=True).start()
        _FFMPEG["running"] = True
    return ok(install=dict(_FFMPEG), tools=tools.status())


# ------------------------------------------------------------------ single instance
def _port_file():
    return os.path.join(app_paths.data_dir(), "port.txt")


def _port_in_use(p: int) -> bool:
    """Instant check. (Connecting to a closed port on Windows takes ~1.5 s to fail,
    so probing ten ports that way made every launch wait ~16 s.)"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", p))
            return False
        except OSError:
            return True


def _running_copy():
    import urllib.request
    import json
    ports = []
    try:
        with open(_port_file(), encoding="utf-8") as f:
            ports.append(int(f.read().strip()))
    except Exception:
        pass
    ports += [p for p in range(DEFAULT_PORT, DEFAULT_PORT + 10) if p not in ports]
    for p in ports:
        if not _port_in_use(p):
            continue
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{p}/api/ping", timeout=1.5) as r:
                if json.loads(r.read().decode()).get("app") == APP_ID:
                    return f"http://127.0.0.1:{p}"
        except Exception:
            continue
    return None


def _pick_port(pref):
    import socket
    for p in range(pref, pref + 30):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    return pref


def _redirect_logs():
    try:
        log = open(os.path.join(app_paths.data_dir(), "mediagrab.log"), "a", encoding="utf-8", buffering=1)
        sys.stdout = sys.stderr = log
    except Exception:
        pass


if __name__ == "__main__":
    if sys.stdout is None or getattr(sys, "frozen", False):
        _redirect_logs()
    open_browser = os.environ.get("MG_NO_BROWSER") != "1"
    if not os.environ.get("PORT"):
        existing = _running_copy()
        if existing:
            if open_browser:
                import webbrowser
                webbrowser.open(existing)
            sys.exit(0)
    port = int(os.environ.get("PORT", "0")) or _pick_port(DEFAULT_PORT)
    try:
        with open(_port_file(), "w", encoding="utf-8") as f:
            f.write(str(port))
    except Exception:
        pass
    downloader.manager()   # resumes any downloads that were interrupted
    print(f"\n  MediaGrab  ->  http://127.0.0.1:{port}\n")
    if open_browser:
        def _open():
            import webbrowser
            time.sleep(1.0)
            webbrowser.open(f"http://127.0.0.1:{port}")
        threading.Thread(target=_open, daemon=True).start()
    app.run(host="127.0.0.1", port=port, threaded=True, debug=False)
