$ErrorActionPreference = "Stop"
Get-Location
$cert=Get-ChildItem -Path Cert:\LocalMachine\My -CodeSigningCert
Set-AuthenticodeSignature -FilePath dist\alcli_setup.msi -Certificate $cert -IncludeChain All
