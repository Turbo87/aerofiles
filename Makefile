test: lint vermin pytest

lint:
	flake8 --exclude=".env,.git,docs" --ignore=E501,W504 .

vermin:
	vermin aerofiles

pytest:
	pytest --cov aerofiles --cov-report term-missing --color=yes

doc:
	cd docs ; make clean html

doc-test:
	cd docs ; make clean html linkcheck

