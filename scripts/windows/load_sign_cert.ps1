$ErrorActionPreference = "Stop"
$decoded = [System.Convert]::FromBase64CharArray($Env:cert, 0, $Env:cert.Length);
$decoded | Set-Content cert.p12 -Encoding Byte;
$Password = ConvertTo-SecureString -String $Env:cert_pwd -AsPlainText -Force
Import-PfxCertificate -FilePath cert.p12 -CertStoreLocation Cert:\LocalMachine\My -Password $Password