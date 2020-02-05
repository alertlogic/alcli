VIRTUAL_ENV_LOCATION := ./alcli_env
VIRTUAL_ENV_ACTIVATE_CMD := $(VIRTUAL_ENV_LOCATION)/bin/activate

BASE := $(shell /bin/pwd)
PYTHON ?= python
PIP ?= pip

.PHONY: dist install uninstall init
.DEFAULT_GOAL := dist

init:
	$(info [+] Installing required packages for '$(NAME)'...")
	@$(PIP) install -r requirements.txt
	$(info [*] Installed required packages for '$(NAME)'...")

test:
	python -m unittest discover -p '*_tests.py' -v -b

lint:
	pycodestyle .

dist:
	$(info [+] Building distribution for '$(NAME)'...")
	@$(PYTHON) setup.py -q sdist
	$(info [+] Build completed.")

pypi_upload: dist
	twine upload --skip-existing dist/alcli-*.*

pypi_test_upload: dist
	twine upload --skip-existing --repository-url https://test.pypi.org/legacy/ dist/alcli-*.*

install: virtualenv
	. $(VIRTUAL_ENV_ACTIVATE_CMD); python setup.py install
	. $(VIRTUAL_ENV_ACTIVATE_CMD); python setup.py clean --all install clean --all

uninstall:
	pip uninstall alcli -y

virtualenv:
	python3 -m venv $(VIRTUAL_ENV_LOCATION)

virtualenv2:
	virtualenv $(VIRTUAL_ENV_LOCATION)

virtual_uninstall:
	rm -rf $(VIRTUAL_ENV_LOCATION)
