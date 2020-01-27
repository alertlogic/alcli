import re
import ast
from setuptools import setup, find_packages

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('alcli/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='alcli',
    version=version,
    url='https://github.com/alertlogic/alcli',
    license='MIT',
    author='Alert Logic Inc.',
    author_email='support@alertlogic.com',
    description='The Alert Logic Command Line Utility (CLI).',
    entry_points = {
        'console_scripts': [
            'alcli = alcli.alertlogic_cli:main'
        ]
    },
    scripts=[],
    packages=find_packages(exclude=['contrib', 'docs', 'tests*', 'troubleshooting']).append('alcli'),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    python_requires='>=3.7',
    install_requires=[
        'alerltlogic-sdk-python>=1.0.1',
        'configparser>=4.0.2',
        'pyyaml==5.1.2'
    ],
    extras_require={
        'dev': [
            'pytest>=3',
            'mock>=2.0.0',
            'httpretty>=0.8.14',
            'pycodestyle>=2.3.1'
        ],
    },
    keywords=['alcli', 'almdr', 'alertlogic']
)
