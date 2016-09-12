all: check test

check:
	@flake8 *.py tests/*.py
	@isort --check -q *.py tests/*.py

test:
	@py.test tests
