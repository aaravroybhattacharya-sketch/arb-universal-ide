; Inno Setup Script for the ARB Language IDE Compiler setup wizard

[Setup]
AppId={{A8F9B2C3-D4E5-4F6A-8B9C-0D1E2F3A4B5C}
AppName=ARB Language Compiler
AppVersion=1.0
AppPublisher=ARB Software
DefaultDirName={autopf}\ARB Compiler
DefaultGroupName=ARB Compiler
AllowNoIcons=yes
; Where to save the final compiled Setup.exe installer wizard
OutputDir=C:\Users\abc\Desktop\Aarav\ARB\installer_output
OutputBaseFilename=ARB_Compiler_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Tells GitHub to look for the application file inside the repository relative folder
Source: "dist\app.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\ARB Compiler"; Filename: "{app}\app.exe"
Name: "{autodesktop}\ARB Compiler"; Filename: "{app}\app.exe"; Tasks: desktopicon

[Run]
Description: "{cm:LaunchProgram,ARB Compiler}"; Flags: nowait postinstall skipifsilent; Filename: "{app}\app.exe"
