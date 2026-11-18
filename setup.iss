; Inno Setup Script for the ARB Universal IDE setup wizard

[Setup]
AppId={{A8F9B2C3-D4E5-4F6A-8B9C-0D1E2F3A4B5C}
AppName=ARB Universal IDE
AppVersion=1.0
AppPublisher=Aarav Roy Bhattacharya
DefaultDirName={autopf}\ARB Universal IDE
DefaultGroupName=ARB Universal IDE
AllowNoIcons=yes
; Where to save the final compiled Setup.exe installer wizard
OutputDir=C:\Users\abc\Desktop\ARB\installer_output
OutputBaseFilename=ARB Universal IDE
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
Name: "{group}\ARB Universal IDE"; Filename: "{app}\app.exe"
Name: "{autodesktop}\ARB Universal IDE"; Filename: "{app}\app.exe"; Tasks: desktopicon

[Run]
Description: "{cm:LaunchProgram,ARB Universal IDE}"; Flags: nowait postinstall skipifsilent; Filename: "{app}\app.exe"
