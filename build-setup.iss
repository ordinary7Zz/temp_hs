[Setup]
AppId={{D7D3E08F-3A0E-4C42-AB8D-4847D0C0B7E1}}   ; 固定 GUID，保证升级覆盖
AppName=毁伤评估软件
AppVersion=1.0.1
DefaultDirName={autopf}\毁伤评估软件
DefaultGroupName=毁伤评估软件
OutputDir=out/setup_dist
OutputBaseFilename=毁伤评估软件v1.0.1-安装向导
UsePreviousAppDir=yes
Uninstallable=yes
UninstallDisplayIcon={app}\main.exe
Compression=lzma
SolidCompression=yes

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "out\dist\main\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\毁伤评估软件"; Filename: "{app}\main.exe"
Name: "{userdesktop}\毁伤评估软件"; Filename: "{app}\main.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "在桌面创建快捷方式"; GroupDescription: "附加任务："; Flags: unchecked
