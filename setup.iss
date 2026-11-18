; Inno Setup Script for the ARB Universal IDE setup wizard

[Setup]
AppId={{A8F9B2C3-D4E5-4F6A-8B9C-0D1E2F3A4B5C}
AppName=ARB Universal IDE
AppVersion=1.0.1
AppPublisher=ARB Software
DefaultDirName={autopf}\ARB Universal IDE
DefaultGroupName=ARB Universal IDE
AllowNoIcons=yes
; Changed to a relative path for GitHub Actions
OutputDir=installer_output
OutputBaseFilename=ARB_Universal_IDE_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=icon\arb_icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Point this exactly to your pyinstaller single executable build
Source: "dist\app.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\ARB Compiler"; Filename: "{app}\app.exe"
Name: "{autodesktop}\ARB Universal IDE"; Filename: "{app}\app.exe"; Tasks: desktopicon

[Run]
Description: "{cm:LaunchProgram,ARB Universal IDE}"; Flags: nowait postinstall skipifsilent; Filename: "{app}\app.exe"
