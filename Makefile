all: lint
.PHONY: all

lint:
	pipenv run flake8 tasks
.PHONY: lint

run:
	pipenv run tasks
.PHONY: run

todo:
	TASKS_STORE=TODO.json pipenv run tasks
.PHONY: todo

dev_install:
	pipenv install --dev
.PHONY: dev_install
