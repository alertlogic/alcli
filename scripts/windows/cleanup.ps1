$ErrorActionPreference = "Stop"
Get-ChildItem build\exe.win-amd64-3.8\ -Filter test -Recurse -Force | Remove-Item -Recurse -Force