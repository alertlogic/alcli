$ErrorActionPreference = "Stop"
$version = Get-Content build_version;
New-Item -Path HKCU:\Software -Name "Jordan Russell";
New-Item -Path "HKCU:\Software\Jordan Russell" -Name "Inno Setup";
New-Item -Path "HKCU:\Software\Jordan Russell\Inno Setup" -Name "SignTools";
$registryPath = "HKCU:\Software\Jordan Russell\Inno Setup\SignTools";
$name = "SignTool0";
$value = "signtool=C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe sign /a /t http://timestamp.verisign.com/scripts/timstamp.dll /sm /s My /n `"Alert Logic`" `$f";
New-ItemProperty -Path $registryPath -Name $name -Value $value;
c:\innosetup\iscc.exe /dMyAppVersion=$version /Odist scripts/windows/alcli_windows_install.iss