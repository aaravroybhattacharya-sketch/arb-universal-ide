[Setup]
AppName=ARB Universal IDE
AppVersion=1.0
DefaultDirName={autopf}\ARB Universal IDE
DefaultGroupName=ARB Universal IDE
OutputDir=installer
OutputBaseFilename=ARB-Universal-IDE-Setup
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\ARB Universal IDE\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\ARB Universal IDE"; Filename: "{app}\ARB Universal IDE.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\ARB Universal IDE"; Filename: "{app}\ARB Universal IDE.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\ARB Universal IDE.exe"; Description: "Launch ARB Universal IDE"; Flags: nowait postinstall skipifsilent
