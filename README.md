# MediaGrab

Download videos, music, thumbnails and images from YouTube, TikTok, Instagram, X, Facebook, Reddit and 1800+ other sites — a local Windows app that runs on your PC with a web UI.

## Features

- **Any quality** — 144p up to 8K, HDR and 60fps, MP4 (plays everywhere) or MKV
- **Audio** — MP3 320/192/128 kbps, M4A, Opus, WAV, with cover art and title embedded
- **Thumbnails & images** — every YouTube thumbnail size, Instagram carousels, X images, Pinterest pins, direct image links
- **Playlists & channels** — pick the videos you want; saved into a folder named after the playlist
- **Batch mode** — paste many links at once
- **Trim** — download only part of a video
- **Any length** — resumable downloads: pause, close the app or lose the connection and it continues where it stopped (auto-retry)
- **Downloads page** — live speed, ETA, pause / resume / cancel / retry / open file / show in folder
- **Settings** — save location, per-site folders, default quality, login cookies (browser or cookies.txt), proxy, speed limit, one-click engine update and FFmpeg install

## Run from source

Requires Python 3.12 and FFmpeg (`winget install Gyan.FFmpeg`).

```
pip install -r requirements.txt
python server.py
```

Then open http://127.0.0.1:5190 (it opens automatically).

## Build the Windows installer

Requires [Inno Setup 6](https://jrsoftware.org/isinfo.php).

```
powershell -ExecutionPolicy Bypass -File build.ps1
```

Produces `installer_output\MediaGrab-Setup.exe`. It ships the official signed Python embeddable runtime with pinned packages (works under Windows Smart App Control) and an uninstaller that runs on the same signed runtime.

## How it works

| File | Role |
| --- | --- |
| `extract.py` | Analyzes a link with yt-dlp (video/audio) and gallery-dl (images), merges the results |
| `downloader.py` | Persistent (SQLite) download queue: resume, retries, temp folders, file validation |
| `server.py` | Flask API + thumbnail proxy |
| `tools.py` | Finds FFmpeg / Deno, updates the engines, installs FFmpeg |
| `static/` | The web interface |
| `uninstall.py` | Smart App Control-safe uninstaller |

Engines: [yt-dlp](https://github.com/yt-dlp/yt-dlp), [gallery-dl](https://github.com/mikf/gallery-dl), [Deno](https://deno.com) (YouTube JavaScript challenges), [curl_cffi](https://github.com/lexiforest/curl_cffi) (TikTok), FFmpeg.

Only download content you have the right to save.
