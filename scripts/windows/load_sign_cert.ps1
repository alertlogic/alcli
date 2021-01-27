$ErrorActionPreference = "Stop"
$decoded = [System.Convert]::FromBase64CharArray($Env:CERT, 0, $Env:CERT.Length);
$decoded | Set-Content cert.p12 -Encoding Byte;
$Password = ConvertTo-SecureString -String $Env:CERT_PWD -AsPlainText -Force
Import-PfxCertificate -FilePath cert.p12 -CertStoreLocation Cert:\LocalMachine\My -Password $Password