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

coverage:
		poetry run pytest --cov=gendiff