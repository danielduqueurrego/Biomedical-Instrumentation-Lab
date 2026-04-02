#define MyAppName "Biomedical Instrumentation Lab"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Biomedical Instrumentation Lab"
#define MyAppExeName "Biomedical Instrumentation Lab.exe"
#define MyArduinoCliDirName "Arduino CLI"
#define MyArduinoCliExeName "arduino-cli.exe"
#define MyArduinoCliMarkerName "biomed_lab_cli_bundle_marker.txt"

[Setup]
AppId={{E590AE16-8A4C-4685-BF48-8A717D0D1F9F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\..\dist\installer
OutputBaseFilename=BiomedicalInstrumentationLabSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"
Name: "installarduino"; Description: "Install bundled Arduino CLI and add it to PATH"; GroupDescription: "Arduino support:"

[Files]
Source: "..\..\dist\Biomedical Instrumentation Lab\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\dist\installer-payload\arduino-cli\*"; DestDir: "{autopf}\{#MyArduinoCliDirName}"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist uninsneveruninstall; Tasks: installarduino
Source: "arduino_cli_bundle_marker.txt"; DestDir: "{autopf}\{#MyArduinoCliDirName}"; DestName: "{#MyArduinoCliMarkerName}"; Flags: ignoreversion uninsneveruninstall; Tasks: installarduino

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; \
    ValueType: expandsz; ValueName: "ARDUINO_CLI"; ValueData: "{autopf}\{#MyArduinoCliDirName}\{#MyArduinoCliExeName}"; \
    Tasks: installarduino

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
const
  MyWM_SETTINGCHANGE = $001A;
  MySMTO_ABORTIFHUNG = $0002;
  EnvironmentSubkey = 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment';
  RemoveArduinoCliSwitch = '/REMOVEARDUINOCLI';
  KeepArduinoCliSwitch = '/KEEPARDUINOCLI';

var
  RemoveArduinoCliOnUninstall: Boolean;
  ArduinoCliRemovalChoiceMade: Boolean;

function SendMessageTimeout(hWnd: Integer; Msg: Integer; wParam: Integer; lParam: String;
  fuFlags: Integer; uTimeout: Integer; out lpdwResult: Integer): Integer;
  external 'SendMessageTimeoutW@user32.dll stdcall';

function NeedsArduinoCliInstall: Boolean;
begin
  Result := not FileExists(ExpandConstant('{autopf}\{#MyArduinoCliDirName}\{#MyArduinoCliExeName}'));
end;

function BundledArduinoCliExists: Boolean;
begin
  Result :=
    FileExists(ExpandConstant('{autopf}\{#MyArduinoCliDirName}\{#MyArduinoCliExeName}')) and
    FileExists(ExpandConstant('{autopf}\{#MyArduinoCliDirName}\{#MyArduinoCliMarkerName}'));
end;

function CommandLineContains(SwitchName: string): Boolean;
begin
  Result := Pos(Uppercase(SwitchName), Uppercase(GetCmdTail)) > 0;
end;

function PathContains(Needle, Haystack: string): Boolean;
begin
  Result := Pos(';' + Uppercase(Needle) + ';', ';' + Uppercase(Haystack) + ';') > 0;
end;

procedure AddDirToSystemPath(DirName: string);
var
  CurrentPath: string;
  NewPath: string;
  ResultCode: Integer;
begin
  if not RegQueryStringValue(HKLM, EnvironmentSubkey, 'Path', CurrentPath) then
    CurrentPath := '';

  if PathContains(DirName, CurrentPath) then
    exit;

  if CurrentPath = '' then
    NewPath := DirName
  else
    NewPath := CurrentPath + ';' + DirName;

  RegWriteExpandStringValue(HKLM, EnvironmentSubkey, 'Path', NewPath);
  SendMessageTimeout(HWND_BROADCAST, MyWM_SETTINGCHANGE, 0, 'Environment', MySMTO_ABORTIFHUNG, 5000, ResultCode);
end;

procedure RemoveDirFromSystemPath(DirName: string);
var
  CurrentPath: string;
  UpdatedPath: string;
  Prefix: string;
  Suffix: string;
  MatchPos: Integer;
  SearchValue: string;
  ResultCode: Integer;
begin
  if not RegQueryStringValue(HKLM, EnvironmentSubkey, 'Path', CurrentPath) then
    exit;

  SearchValue := ';' + DirName;
  MatchPos := Pos(Uppercase(SearchValue), Uppercase(';' + CurrentPath));
  if MatchPos = 0 then
    exit;

  Prefix := Copy(CurrentPath, 1, MatchPos - 1);
  Suffix := Copy(CurrentPath, MatchPos + Length(SearchValue), MaxInt);

  if (Suffix <> '') and (Suffix[1] = ';') then
    Delete(Suffix, 1, 1);

  if (Prefix <> '') and (Prefix[Length(Prefix)] = ';') then
    Delete(Prefix, Length(Prefix), 1);

  if (Prefix <> '') and (Suffix <> '') then
    UpdatedPath := Prefix + ';' + Suffix
  else
    UpdatedPath := Prefix + Suffix;

  RegWriteExpandStringValue(HKLM, EnvironmentSubkey, 'Path', UpdatedPath);
  SendMessageTimeout(HWND_BROADCAST, MyWM_SETTINGCHANGE, 0, 'Environment', MySMTO_ABORTIFHUNG, 5000, ResultCode);
end;

procedure RemoveArduinoCliRegistration;
var
  ResultCode: Integer;
begin
  RemoveDirFromSystemPath(ExpandConstant('{autopf}\{#MyArduinoCliDirName}'));
  RegDeleteValue(HKLM, EnvironmentSubkey, 'ARDUINO_CLI');
  SendMessageTimeout(HWND_BROADCAST, MyWM_SETTINGCHANGE, 0, 'Environment', MySMTO_ABORTIFHUNG, 5000, ResultCode);
end;

procedure MaybeAskAboutArduinoCliRemoval;
var
  PromptResult: Integer;
begin
  if ArduinoCliRemovalChoiceMade then
    exit;

  ArduinoCliRemovalChoiceMade := True;
  RemoveArduinoCliOnUninstall := False;

  if not BundledArduinoCliExists then
    exit;

  if CommandLineContains(KeepArduinoCliSwitch) then
    exit;

  if CommandLineContains(RemoveArduinoCliSwitch) then
  begin
    RemoveArduinoCliOnUninstall := True;
    exit;
  end;

  if UninstallSilent then
    exit;

  PromptResult := SuppressibleMsgBox(
    'Also remove the bundled Arduino CLI from "C:\Program Files\Arduino CLI"?' + #13#10#13#10 +
    'Choose "No" if you want to keep Arduino CLI available for other tools or future installs.',
    mbConfirmation,
    MB_YESNO or MB_DEFBUTTON2,
    IDNO
  );

  RemoveArduinoCliOnUninstall := (PromptResult = IDYES);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssPostInstall) and WizardIsTaskSelected('installarduino') then
    AddDirToSystemPath(ExpandConstant('{autopf}\{#MyArduinoCliDirName}'));
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
    MaybeAskAboutArduinoCliRemoval;

  if CurUninstallStep = usPostUninstall then
  begin
    if RemoveArduinoCliOnUninstall and BundledArduinoCliExists then
    begin
      RemoveArduinoCliRegistration;
      DelTree(ExpandConstant('{autopf}\{#MyArduinoCliDirName}'), True, True, True);
    end;
  end;
end;
