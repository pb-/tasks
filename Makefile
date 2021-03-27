all: lint
.PHONY: all

lint:
	pipenv run flake8 tasks
	pipenv run isort tasks --check --diff
.PHONY: lint

autosort:
	pipenv run isort tasks
.PHONY: autosort

run:
	pipenv run tasks
.PHONY: run

todo:
	TASKS_STORE=TODO.json pipenv run tasks
.PHONY: todo

dev_install:
	pipenv install --dev
.PHONY: dev_install

dist:
	rm -f dist/*
	pipenv run python setup.py sdist bdist_wheel
.PHONY: dist

upload:
	pipenv run twine upload dist/*
.PHONY: upload
