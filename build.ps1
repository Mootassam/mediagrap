# Builds installer_output\MediaGrab-Setup.exe:
#   signed Python embeddable runtime + exact, pinned PyPI wheels (no dependency resolution
#   surprises) + Deno (signed by Deno Land Inc., needed for YouTube).
# Versions are the ones already trusted on this PC so Smart App Control doesn't block their
# native files (curl_cffi / cffi / brotli / pycryptodomex / websockets).
# FFmpeg is used from the PC (winget) — the app offers a one-click "Install FFmpeg" if missing.
#   powershell -ExecutionPolicy Bypass -File build.ps1
$ErrorActionPreference = "Stop"
$root  = $PSScriptRoot
$pyVer = "3.12.10"
$stage = Join-Path $root "build_embed"
$cache = Join-Path $root "build_cache"
$zip   = Join-Path $cache "python-$pyVer-embed-amd64.zip"

New-Item -ItemType Directory -Force $cache | Out-Null
if (-not (Test-Path $zip)) {
    $shared = "D:\cutstudio\build_cache\python-$pyVer-embed-amd64.zip"
    if (Test-Path $shared) { Copy-Item $shared $zip }
    else {
        Write-Host "Downloading Python $pyVer embeddable runtime..."
        Invoke-WebRequest "https://www.python.org/ftp/python/$pyVer/python-$pyVer-embed-amd64.zip" -OutFile $zip -UseBasicParsing
    }
}
if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }
$rt  = Join-Path $stage "runtime"
$app = Join-Path $stage "app"
Expand-Archive $zip $rt
$pth = @("python312.zip", ".", "Lib\site-packages", "..\app", "import site") -join "`r`n"
[IO.File]::WriteAllText((Join-Path $rt "python312._pth"), $pth + "`r`n")
$sp = Join-Path $rt "Lib\site-packages"

Write-Host "Installing pinned packages..."
python -m pip install --disable-pip-version-check --no-cache-dir --only-binary=:all: --no-deps `
    --platform win_amd64 --python-version 3.12 --implementation cp --target $sp `
    flask==3.1.3 werkzeug==3.1.8 jinja2==3.1.6 markupsafe==3.0.3 itsdangerous==2.2.0 `
    click==8.5.0 blinker==1.9.0 colorama==0.4.6 `
    requests==2.34.2 certifi==2026.7.22 charset-normalizer==3.5.1 idna==3.20 urllib3==2.8.0 `
    yt-dlp==2026.8.19 yt-dlp-ejs==0.8.0 brotli==1.2.0 mutagen==1.48.1 pycryptodomex==3.24.0 `
    websockets==17.2 curl-cffi==0.16.3 cffi==2.1.1 pycparser==3.0 typing-extensions==4.16.0 `
    gallery-dl==1.32.16 deno==2.9.7 pip==26.2.1
if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
if (-not (Test-Path (Join-Path $sp "bin\deno.exe"))) { throw "deno.exe missing from the staged runtime" }

New-Item -ItemType Directory -Force $app | Out-Null
Copy-Item (Join-Path $root "*.py") $app
Copy-Item (Join-Path $root "mediagrab.ico") $app
Copy-Item -Recurse (Join-Path $root "static") (Join-Path $app "static")
New-Item -ItemType File (Join-Path $app ".installed") | Out-Null

# smoke test: everything imports in the staged runtime and Deno is found and runs
$check = "import sys; sys.path.insert(0, r'$app'); " +
         "import flask, requests, yt_dlp, yt_dlp_ejs, curl_cffi, brotli, mutagen, Cryptodome, websockets, gallery_dl, " +
         "app_paths, config, tools, extract, downloader, server; " +
         "import subprocess; d = tools.deno_path(); assert d and 'site-packages' in d, d; " +
         "print('deno', subprocess.run([d, '--version'], capture_output=True, text=True).stdout.split()[1]); print('imports ok')"
& (Join-Path $rt "python.exe") -c $check
if ($LASTEXITCODE -ne 0) { throw "staged runtime cannot import the app" }
Get-ChildItem $stage -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

$iscc = Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $iscc)) { $iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe" }
& $iscc (Join-Path $root "installer.iss")
if ($LASTEXITCODE -ne 0) { throw "ISCC failed" }
Get-Item (Join-Path $root "installer_output\MediaGrab-Setup.exe") | Select-Object FullName, Length
