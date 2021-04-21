$ErrorActionPreference = "Stop"
$PyPath=python -c 'import sys; import os; print(os.path.dirname(sys.executable))'
(Get-Content $PyPath\Lib\site-packages\jsonschema\__init__.py) | ForEach-Object { $_ -replace "try.+" , "" } | Set-Content $PyPath\Lib\site-packages\jsonschema\__init__.py
(Get-Content $PyPath\Lib\site-packages\jsonschema\__init__.py) | ForEach-Object { $_ -replace "from importlib import.+" , "" } | Set-Content $PyPath\Lib\site-packages\jsonschema\__init__.py;
(Get-Content $PyPath\Lib\site-packages\jsonschema\__init__.py) | ForEach-Object { $_ -replace "except ImportError.+" , "" } | Set-Content $PyPath\Lib\site-packages\jsonschema\__init__.py;
(Get-Content $PyPath\Lib\site-packages\jsonschema\__init__.py) | ForEach-Object { $_ -replace "import importlib_metadata.+" , "" } | Set-Content $PyPath\Lib\site-packages\jsonschema\__init__.py;
(Get-Content $PyPath\Lib\site-packages\jsonschema\__init__.py) | ForEach-Object { $_ -replace "__version__.+" , "__version__ = '3.2.0'" } | Set-Content $PyPath\Lib\site-packages\jsonschema\__init__.py