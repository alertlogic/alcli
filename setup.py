import re
import ast
from os import path
from setuptools import setup, find_packages

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('alcli/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
        'alertlogic-sdk-python>=1.0.13',
        'configparser>=4.0.2',
        'pyyaml==5.1.2',
        'jmespath>=0.9.4'
    ]
setup(
    name='alcli',
    version=version,
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
    keywords=['alcli', 'almdr', 'alertlogic', 'alertlogic-cli']
)
