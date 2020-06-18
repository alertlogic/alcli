$ErrorActionPreference = "Stop"
$version = Get-Content build_version;
$product_version = '/pv ' + $version;
Start-Process '.\verpatch\verpatch.exe' -ArgumentList '.\build\exe.win-amd64-3.8\alcli.exe', $version, '/va', $product_version, '/langid 1033', '/s desc "Alert Logic CLI"', '/s copyright "Copyright (C) 2020, Alert Logic, Inc."', '/s product "Alert Logic CLI"'