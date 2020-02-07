# Installing the Alert Logic CLI
The `pip` package manager for Python is used to install, upgrade and remove Alert Logic CLI.

## **Installing the current version of the Alert Logic CLI**

Alert Logic CLI only works on Python 3.7 or higher. 
Please follow this instructions on how to install Python on your system: <https://www.python.org/downloads/>


Use `pip3` to install the Alert Logic CLI

    $ pip3 install alcli --upgrade --user


Make sure to use `--user` to to install the program to a subdirectory of your user directory to avoid modifying libraries used by your operating system.

## **Upgrading to the latest version of the Alert Logic CLI**
We regularly introduce support for new Alert Logic services.
We recommend that you check installed packages version and upgrade to the latest version regularly

    $ alcli --version
    
	$ pip3 list -o
	Package    				Version  Latest   Type 
	---------- 				-------- -------- -----
	alcli     				1.0.1 	 1.0.2 	  sdist
	alertlogic-sdk-python   1.0.2 	 1.0.2    sdist
	
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

