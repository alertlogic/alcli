$ErrorActionPreference = "Stop"
$version = Get-Content build_version;
New-Item -Path HKCU:\Software -Name "Jordan Russell";
New-Item -Path "HKCU:\Software\Jordan Russell" -Name "Inno Setup";
New-Item -Path "HKCU:\Software\Jordan Russell\Inno Setup" -Name "SignTools";
$registryPath = "HKCU:\Software\Jordan Russell\Inno Setup\SignTools";
$name = "SignTool0";
$value = "`$cert=Get-ChildItem -Path Cert:\LocalMachine\My -CodeSigningCert Set-AuthenticodeSignature -FilePath `$f -Certificate $cert -IncludeChain All -TimestampServer `"http://timestamp.fabrikam.com/scripts/timstamper.dll`"";
New-ItemProperty -Path $registryPath -Name $name -Value $value;
c:\innosetup\iscc.exe /dMyAppVersion=$version /Odist scripts/windows/alcli_windows_install.iss