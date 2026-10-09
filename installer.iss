; MediaGrab installer — ships the official, digitally signed Python runtime (Python Software
; Foundation) + pinned libraries + Deno (signed by Deno Land Inc.), so Smart App Control can
; verify what it runs. FFmpeg comes from the PC (the app can install it with winget).
; Build: powershell -ExecutionPolicy Bypass -File build.ps1

#define MyAppName "MediaGrab"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "MediaGrab"

[Setup]
AppId={{5E1B7C42-9D3A-4C6E-8F21-MEDIAGRAB0001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
DisableDirPage=auto
OutputDir=installer_output
OutputBaseFilename=MediaGrab-Setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible
SetupIconFile=mediagrab.ico
UninstallDisplayIcon={app}\app\mediagrab.ico
UninstallDisplayName={#MyAppName}
CloseApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; Flags: checkedonce

[InstallDelete]
Type: filesandordirs; Name: "{app}\app"
Type: filesandordirs; Name: "{app}\runtime"

[Files]
Source: "build_embed\runtime\*"; DestDir: "{app}\runtime"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "build_embed\app\*"; DestDir: "{app}\app"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\runtime\pythonw.exe"; Parameters: """{app}\app\server.py"""; WorkingDir: "{app}\app"; IconFilename: "{app}\app\mediagrab.ico"; Comment: "Download videos, music, thumbnails and images"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\runtime\pythonw.exe"; Parameters: """{app}\app\server.py"""; WorkingDir: "{app}\app"; IconFilename: "{app}\app\mediagrab.ico"; Tasks: desktopicon
; Uninstall via the signed runtime — works even under Smart App Control, which blocks Inno's unins000.exe.
Name: "{autoprograms}\Uninstall {#MyAppName}"; Filename: "{app}\runtime\pythonw.exe"; Parameters: """{app}\app\uninstall.py"""; WorkingDir: "{app}\app"; IconFilename: "{app}\app\mediagrab.ico"; Comment: "Remove {#MyAppName}"

[Run]
; first-run preparation: load every component once now so the app opens instantly afterwards
Filename: "{app}\runtime\python.exe"; Parameters: "-c ""import yt_dlp, yt_dlp_ejs, curl_cffi, gallery_dl, flask, requests, tools, extract, downloader; import subprocess; subprocess.run([tools.deno_path(), '--version'], capture_output=True)"""; WorkingDir: "{app}\app"; StatusMsg: "Preparing MediaGrab..."; Flags: runhidden waituntilterminated
Filename: "{app}\runtime\pythonw.exe"; Parameters: """{app}\app\server.py"""; WorkingDir: "{app}\app"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
procedure StopMediaGrab();
var
  Rc: Integer;
  Cmd, AppDir: String;
begin
  AppDir := Lowercase(ExpandConstant('{app}'));
  Cmd := '-NoProfile -ExecutionPolicy Bypass -Command "Get-Process python,pythonw,deno -ErrorAction SilentlyContinue | ' +
         'Where-Object { $_.Path -and $_.Path.ToLower().StartsWith(''' + AppDir + ''') } | ' +
         'Stop-Process -Force -ErrorAction SilentlyContinue; Start-Sleep -Milliseconds 900"';
  Exec(ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe'), Cmd, '', SW_HIDE, ewWaitUntilTerminated, Rc);
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  StopMediaGrab();
  Result := '';
end;

function InitializeUninstall(): Boolean;
begin
  StopMediaGrab();
  Result := True;
end;

{ Point Windows "Apps > Uninstall" at uninstall.py run by the signed Python runtime: Inno's unins000.exe
  is unsigned and generated at install time, so Smart App Control blocks it; python.exe is signed by the
  PSF and runs. Written in ssPostInstall so it overrides Inno's own registration. }
procedure CurStepChanged(CurStep: TSetupStep);
var
  Key, Pyw, Py, Script: String;
begin
  if CurStep = ssPostInstall then
  begin
    { single-brace literal on purpose: [Code] string literals are not constant-expanded }
    Key := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{5E1B7C42-9D3A-4C6E-8F21-MEDIAGRAB0001}_is1';
    Pyw := ExpandConstant('{app}\runtime\pythonw.exe');
    Py  := ExpandConstant('{app}\runtime\python.exe');
    Script := ExpandConstant('{app}\app\uninstall.py');
    RegWriteStringValue(HKCU, Key, 'UninstallString', '"' + Pyw + '" "' + Script + '"');
    RegWriteStringValue(HKCU, Key, 'QuietUninstallString', '"' + Py + '" "' + Script + '" /quiet');
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataDir := ExpandConstant('{localappdata}\MediaGrab');
    if DirExists(DataDir) and not UninstallSilent() then
      if MsgBox('Also delete your MediaGrab settings and download history?' + #13#10 + #13#10 +
                'Your downloaded videos, music and images are NOT touched - they stay in your Downloads folder.' + #13#10 + #13#10 +
                'Choose No to keep your settings for a future reinstall.',
                mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
        DelTree(DataDir, True, True, True);
  end;
end;

[UninstallDelete]
Type: filesandordirs; Name: "{app}\app"
Type: filesandordirs; Name: "{app}\runtime"
Type: dirifempty; Name: "{app}"
