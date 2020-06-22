$ErrorActionPreference = "Stop"
wget https://jrsoftware.org/download.php/is.exe -o is.exe
Start-Process is.exe -ArgumentList '/VERYSILENT', '/ALLUSERS', '/DIR=c:\innosetup' -NoNewWindow -Wait
