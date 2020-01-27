VIRTUAL_ENV_LOCATION := ./alcli_env
VIRTUAL_ENV_ACTIVATE_CMD := $(VIRTUAL_ENV_LOCATION)/bin/activate

.PHONY: dist install uninstall init
.DEFAULT_GOAL := dist

init:
	pip install -r requirements.txt

test:
	python -m unittest discover -p '*_tests.py' -v -b

lint:
	pycodestyle .

dist:
	python setup.py sdist

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
