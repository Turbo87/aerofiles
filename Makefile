all: lint vermin pytest

test: pytest

lint:
	flake8 --exclude=".env,.git,docs" --ignore=E501,W503,W504 aerofiles tests

lint-fix:
	autopep8 --in-place --recursive aerofiles tests

vermin:
	vermin aerofiles

pytest:
	pytest --cov aerofiles --cov-report term-missing --color=yes

doc:
	cd docs ; make clean html

doc-test:
	cd docs ; make clean html linkcheck

