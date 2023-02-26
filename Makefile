install_wmflabs:
	webservice --backend=kubernetes python3.5 stop
	pip install poetry
	poetry install --no-dev

install_development:
	pip install poetry
	poetry install

test:
	flake8 --config=setup.cfg
	pytest --disable-warnings

restart:
	flask db upgrade
	webservice --backend=kubernetes python3.5 start
