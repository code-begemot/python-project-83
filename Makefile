install:
	poetry install
dev:
	poetry run flask --app page_analyzer:app run
my_dev:
	psql postgresql-database -f database.sql && poetry run flask --app page_analyzer:app --debug run --port 8000
PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
lint:
	poetry run flake8 page_analyzer
test:
	poetry run pytest

test-coverage:
	poetry run pytest --cov=page_analyzer --cov-report xml

selfcheck:
	poetry check

check: selfcheck test lint

build:
	./build.sh

.PHONY: install test lint selfcheck check build
