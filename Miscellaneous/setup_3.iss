; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "NHL Goal Horn Scoreboard"
#define MyAppVersion "2.0.0.0"
#define MySetupVersion "1.0.0.0"
#define MyAppPublisher "Austin Chen"
#define MyAppURL "austinandemily.com"
#define MyAppExeName "NHL Goal Horn Scoreboard.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{8B94A1D8-3A14-43AF-87A2-BE83E685367E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName ={#MyAppName}
AppPublisher={#MyAppPublisher}
;AppPublisherURL={#MyAppURL}
;AppSupportURL={#MyAppURL}
;AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
VersionInfoCompany={#MyAppPublisher}
VersionInfoCopyright=Copyright (C) 2016 Austin Chen
;VersionInfoDescription
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoVersion={#MySetupVersion}
;VersionInfoTextVersion=
DisableProgramGroupPage=yes
OutputBaseFilename=NHL Goal Horn Scoreboard Setup
SetupIconFile=C:\Users\chena\Desktop\NHL Goal Horn Scoreboard\Assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
;WelcomeLabel2=This will install [name/ver] on your computer.%n%nIt is recommended that you close all other applications and disable any anti virus before continuing.
SetupAppTitle=NHL Goal Horn Scoreboard Setup
SetupWindowTitle=NHL Goal Horn Scoreboard Setup
UninstallAppTitle=Uninstall NHL Goal Horn Scoreboard
UninstallAppFullTitle=Uninstall NHL Goal Horn Scoreboard

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "C:\Users\chena\Desktop\NHL Goal Horn Scoreboard\dist\NHL Goal Horn Scoreboard.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\chena\Desktop\NHL Goal Horn Scoreboard\dist\python27.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\chena\Desktop\NHL Goal Horn Scoreboard\dist\Python Resources\*"; DestDir: "{app}\Python Resources\"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\chena\Desktop\NHL Goal Horn Scoreboard\Assets\*"; DestDir: "{app}\Assets\"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\chena\Desktop\NHL Goal Horn Scoreboard\Assets\Fonts\Trade Gothic Bold.ttf"; DestDir: "{fonts}"; FontInstall: "Trade Gothic Bold"; Flags: onlyifdoesntexist uninsneveruninstall
Source: "C:\Users\chena\Desktop\NHL Goal Horn Scoreboard\Assets\Fonts\Trade Gothic Light.ttf"; DestDir: "{fonts}"; FontInstall: "Trade Gothic Light"; Flags: onlyifdoesntexist uninsneveruninstall
Source: "C:\Users\chena\Desktop\NHL Goal Horn Scoreboard\Assets\Fonts\Consolas.ttf"; DestDir: "{fonts}"; FontInstall: "Consolas"; Flags: onlyifdoesntexist uninsneveruninstall
Source: "C:\Users\chena\Desktop\NHL Goal Horn Scoreboard\Development\Installer\vcredist_x86.exe"; DestDir: {tmp}; Flags: deleteafterinstall
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{commonprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: {tmp}\vcredist_x86.exe; Parameters: "/q:a /c:""VCREDI~3.EXE /q:a /c:""""msiexec /i vcredist.msi /qn"""" """; StatusMsg: Installing Microsoft Visual C++ 2008 Redistributable...;
;Filename: {tmp}\vcredist_x86.exe; Parameters: "/q /passive /Q:a /c:""msiexec /q /i vcredist.msi"" "; StatusMsg: Installing VC++ 2008 Redistributables...
;Filename: {src}\Redistributables\vcredist_x86.exe; Parameters: "/q:a /c:""VCREDI~3.EXE /q:a /c:""""msiexec /i vcredist.msi /qn"""" """;
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent