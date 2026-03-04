#define MyAppName "DJ Selector"
#ifndef AppVersion
  #define AppVersion "0.1.0"
#endif
#define MyAppPublisher "DJ Selector App"
#define MyAppExeName "DJSelector.exe"

[Setup]
AppId={{0D4D9D44-3D9E-44B7-B8B6-E5F4F4D603A1}
AppName={#MyAppName}
AppVersion={#AppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\DJ Selector
DefaultGroupName=DJ Selector
OutputDir=output
OutputBaseFilename=DJSelector-Setup-{#AppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "..\..\dist\DJSelector\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{autoprograms}\DJ Selector"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\DJ Selector"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch DJ Selector"; Flags: nowait postinstall skipifsilent
