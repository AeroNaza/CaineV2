[Setup]
AppName=Caine
AppVersion=2.0
DefaultDirName={autopf}\Caine
DefaultGroupName=Caine
OutputDir=Output
OutputBaseFilename=CaineSetup
SetupIconFile=assets\Cainelogo.ico
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest

[Files]
Source: "dist\Caine.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\Cainelogo.png"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\Caine"; Filename: "{app}\Caine.exe"
Name: "{autodesktop}\Caine"; Filename: "{app}\Caine.exe"

[Run]
Filename: "{app}\Caine.exe"; Description: "Abrir Caine"; Flags: nowait postinstall skipifsilent
