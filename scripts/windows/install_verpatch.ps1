$ErrorActionPreference = "Stop"
wget https://s3.amazonaws.com/alertlogic-public-repo.us-east-1/alcli-win-install/thirdparty/verpatch-1.0.15.1-x86-codeplex.zip -o verpatch-1.0.15.1-x86-codeplex.zip
powershell -Command expand-archive -path 'verpatch-1.0.15.1-x86-codeplex.zip' -destinationpath '.\verpatch'
