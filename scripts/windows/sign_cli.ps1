$ErrorActionPreference = "Stop"
Get-Location
& 'C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe' sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 /a /s My /debug /n "Alert Logic" /v build\exe.win-amd64-3.8\alcli.exe
#& 'C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe' sign /a /t http://timestamp.digicert.com /sm /s My /debug /n "Alert Logic" /v build\exe.win-amd64-3.8\alcli.exe
& 'C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe' verify /pa build\exe.win-amd64-3.8\alcli.exe
