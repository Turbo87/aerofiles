test: lint vermin pytest

lint:
	flake8 --exclude=".git,docs" --ignore=E501,W504 .

vermin:
	vermin aerofiles

pytest:
	pytest --cov aerofiles --cov-report term-missing --color=yes

