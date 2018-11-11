all: lint
.PHONY: all

lint:
	pipenv run flake8 tasks
.PHONY: lint

run:
	pipenv run tasks
.PHONY: run

dev_install:
	pipenv install --dev
.PHONY:
