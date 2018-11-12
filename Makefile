all: lint
.PHONY: all

lint:
	pipenv run flake8 tasks
	pipenv run isort -c
.PHONY: lint

autosort:
	pipenv run isort -y
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
