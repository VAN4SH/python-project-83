install:
	poetry install -n -v --no-root

lint:
	poetry run flake8 page_analyzer

dev:
	poetry run flask --app page_analyzer:app --debug run 

PORT ?= 8000

start:
	poetry run gunicorn -w 2 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh


