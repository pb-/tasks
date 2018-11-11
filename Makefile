all: check test

check:
	@flake8 *.py tests/*.py
	@isort --check -q *.py tests/*.py
.PHONY: check

test:
	@py.test tests
.PHONY: test
