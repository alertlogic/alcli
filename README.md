
[![Build Status](https://github.com/alertlogic/alcli/actions/workflows/release_pypi.yml/badge.svg)](https://github.com/alertlogic/alcli/actions)
[![Windows Build](https://github.com/alertlogic/alcli/actions/workflows/windows_build.yml/badge.svg)](https://github.com/alertlogic/alcli/actions)
[![PyPI version](https://badge.fury.io/py/alcli.svg)](https://badge.fury.io/py/alcli)

# Installing the Alert Logic CLI
The `pip` package manager for Python is used to install, upgrade and remove Alert Logic CLI.

## **Installing the current version of the Alert Logic CLI**

Alert Logic CLI only works on Python 3.8 or higher.
Please follow this instructions on how to install Python on your system: <https://www.python.org/downloads/>


Use `pip3` to install the Alert Logic CLI

    $ pip3 install alcli --upgrade --user


Make sure to use `--user` to to install the program to a subdirectory of your user directory to avoid modifying libraries used by your operating system.

### Windows installer

For windows users there is self-contained Alert Logic CLI distribution is available, please download latest version from here: 
* [executable installation package](https://github.com/alertlogic/alcli/releases/latest/download/AlertlogicCLISetup.exe)
* [msi installation package](https://github.com/alertlogic/alcli/releases/latest/download/AlertlogicCLISetup.msi)

Alternatively, please view [history](https://github.com/alertlogic/alcli/releases/) of the releases. 

## **Upgrading to the latest version of the Alert Logic CLI**
We regularly introduce support for new Alert Logic services.
We recommend that you check installed packages version and upgrade to the latest version regularly.

```
$ pip3 install --upgrade --force-reinstall alcli
```

## Configure the Alert Logic CLI with Your Credentials
Before you can run a CLI command, you must configure the Alert Logic's CLI with your credentials.

By default, `alcli` uses ~/.alertlogic/config configuration file in a user's home directory. File can contain multiple profiles. Here's an example of a configuration file that has credentials for an integration and production deployments:

    [default]
	access_key_id=1111111111111111
	secret_key=eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
	global_endpoint=integration
	
	[production]
	access_key_id=2222222222222222
	secret_key=dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd
	global_endpoint=production


The location of the configuration file can be also specified by setting `ALERTLOGIC_CONFIG` environment variable to contain file's location.

## Notes:
`--query` option requires JMESPath language expression. See 
<http://jmespath.org/tutorial.html> for language tutorial.

