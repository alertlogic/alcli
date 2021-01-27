$ErrorActionPreference = "Stop"
Get-Location
& 'C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe' sign /a /t http://timestamp.globalsign.com/scripts/timstamp.dll /sm /s My /debug /n "Alert Logic" /v dist\alcli.msi
& 'C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe' verify /pa dist\alcli.msi
