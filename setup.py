import re
import ast
import sys
from urllib import request
import json

from setuptools import setup, find_packages
if sys.platform == 'win32':
    from cx_Freeze import setup, Executable
    base = None
    executables = [Executable(
            script='alcli/alertlogic_cli.py',
            targetName='alcli',
            base=base,
            icon='icons/alertlogic-win.ico'
            )
        ]
else:
    executables = []

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

try:
    # This is to force definitions to be upgraded every build not related to the definitions change
    sdk_pypi_url = "https://pypi.org/pypi/alertlogic-sdk-python/json"
    with request.urlopen(sdk_pypi_url) as defs_rq:
        defs_info = json.loads(defs_rq.read())
    sdk_latest_version = defs_info['info']['version']
    sdk_dependency = 'alertlogic-sdk-python>=' + sdk_latest_version
except:
    sdk_dependency = 'alertlogic-sdk-python>=v1.0.47'

requirements = [
        sdk_dependency,
        'configparser==4.0.2',
        'pyyaml==5.1.2',
        'jmespath==0.9.4',
        'importlib_metadata==1.6.0'
    ]
setup(
    name='alcli',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    url='https://github.com/alertlogic/alcli',
    license='MIT license',
    author='Alert Logic Inc.',
    author_email='devsupport@alertlogic.com',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    description='The Alert Logic Command Line Utility (CLI).',
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',
    entry_points = {
        'console_scripts': [
            'alcli = alcli.alertlogic_cli:main'
        ]
    },
    scripts=[],
    packages=find_packages(exclude=['contrib', 'docs', 'tests*', 'troubleshooting']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=3',
            'mock>=2.0.0',
            'httpretty>=0.8.14',
            'pycodestyle>=2.3.1'
        ],
    },
    options = {
        'build_exe': {
            'packages': ['os', 'sys', 'ctypes', 'jsonschema', 'almdrlib', 'alcli'],
            'excludes': ['tkinter','tcl','ttk'],
            'include_msvcr': True
        },
        'bdist_msi': {
            'add_to_path': False
        }
    },
    executables = executables,
    keywords=['alcli', 'almdr', 'alertlogic', 'alertlogic-cli']
)
