check:
	@flake8 *.py tests/*.py
	@isort --check -q *.py tests/*.py
