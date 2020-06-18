[Code]
const GlobalEnvironmentKey = 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment';
const UserEnvironmentKey = 'Environment';

function EndsWith(SubText, Text: string): Boolean;
var
  EndStr: string;
begin
  EndStr := Copy(Text, Length(Text) - Length(SubText) + 1, Length(SubText));
  Result := SameText(SubText, EndStr);
end;

procedure EnvAddPath(Path: string);
var
    Paths: string;
    RootKey: integer;
    EnvironmentKey: string;
begin
    if IsAdminInstallMode then begin
      EnvironmentKey := GlobalEnvironmentKey
      RootKey := HKEY_LOCAL_MACHINE
    end else begin
      EnvironmentKey := UserEnvironmentKey
      RootKey := HKEY_CURRENT_USER
    end;
      
    { Retrieve current path (use empty string if entry not exists) }
    if not RegQueryStringValue(RootKey, EnvironmentKey, 'Path', Paths)
    then Paths := '';

    { Skip if string already found in path }
    if Pos(';' + Uppercase(Path) + ';', ';' + Uppercase(Paths) + ';') > 0 then exit;

    { App string to the end of the path variable }
    if EndsWith(';', Paths)
    then Paths := Paths + Path +';' 
    else Paths := Paths + ';'+ Path +';';

    { Overwrite (or create if missing) path environment variable }
    if RegWriteStringValue(RootKey, EnvironmentKey, 'Path', Paths)
    then Log(Format('The [%s] added to PATH: [%s]', [Path, Paths]))
    else Log(Format('Error while adding the [%s] to PATH: [%s]', [Path, Paths]));
end;

procedure EnvRemovePath(Path: string);
var
    Paths: string;
    RootKey: integer;
    EnvironmentKey: string;
    P: Integer;
begin

    if IsAdminInstallMode then begin
      EnvironmentKey := GlobalEnvironmentKey
      RootKey := HKEY_LOCAL_MACHINE
    end else begin
      EnvironmentKey := UserEnvironmentKey
      RootKey := HKEY_CURRENT_USER
    end;

    { Skip if registry entry not exists }
    if not RegQueryStringValue(RootKey, EnvironmentKey, 'Path', Paths) then
        exit;

    { Skip if string not found in path }
    P := Pos(';' + Uppercase(Path) + ';', ';' + Uppercase(Paths) + ';');
    if P = 0 then exit;

    { Update path variable }
    Delete(Paths, P - 1, Length(Path) + 1);

    { Overwrite path environment variable }
    if RegWriteStringValue(RootKey, EnvironmentKey, 'Path', Paths)
    then Log(Format('The [%s] removed from PATH: [%s]', [Path, Paths]))
    else Log(Format('Error while removing the [%s] from PATH: [%s]', [Path, Paths]));
end;
