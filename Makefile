install:
	poetry install
dev:
	poetry run flask --app page_analyzer:app run
PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
lint:
	poetry run flake8 page_analyzer
test:
	poetry run pytest

test-coverage:
	poetry run pytest --cov=gendiff --cov-report xml