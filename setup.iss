[Setup]
AppName=ARB Universal IDE
AppVersion=latest
DefaultDirName={autopf}\ARB Universal IDE
DefaultGroupName=ARB Universal IDE
OutputDir=installer_output
OutputBaseFilename=ARB_Universal_IDE
SetupIconFile=icon\arb_icon.ico
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\app\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icon\arb_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\ARB Universal IDE"; Filename: "{app}\app.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\ARB Universal IDE"; Filename: "{app}\app.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\app.exe"; Description: "Launch ARB Universal IDE"; Flags: nowait postinstall skipifsilent
