$ErrorActionPreference = "Stop"
Get-Location
$cert=Get-ChildItem -Path Cert:\LocalMachine\My -CodeSigningCert
Set-AuthenticodeSignature -FilePath build\exe.win-amd64-3.8\alcli.exe -Certificate $cert -IncludeChain All