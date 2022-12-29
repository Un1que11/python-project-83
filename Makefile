start:
		poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

dev:
		poetry run flask --app page_analyzer:app run

install:
		poetry install

build:
		poetry build

package-install:
		python3 -m pip install --user dist/*.whl

lint:
		poetry run flake8 page_analyzer

reinstall:
		pip install --user --force-reinstall dist/*.whl

test:
		poetry run pytest -v

test-coverage:
		poetry run pytest --cov=page_analyzer --cov-report xml