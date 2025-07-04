
# Directories inside aerofiles, containing python code that should
# comply with python 26/3.0:
SRC_DIR_PY_26_30 = igc flarmcfg openair seeyou util welt2000 xcsoar

# Directories inside aerofiles, containing python code that should
# comply with python 27:
SRC_DIR_PY_37 = aixm

all: lint vermin pytest

test: pytest

lint:
	flake8 --exclude=".env,.git,docs" --ignore=E501,W503,W504 aerofiles tests

lint-fix:
	autopep8 --in-place --recursive aerofiles tests

vermin:
	vermin --target=2.6 --target=3.0 $(addprefix aerofiles/,$(SRC_DIR_PY_26_30))
	vermin --target=3.7 $(addprefix aerofiles/,$(SRC_DIR_PY_37))

pytest:
	pytest --cov aerofiles --cov-report term-missing --color=yes

doc:
	cd docs ; make clean html

doc-test:
	cd docs ; make clean html linkcheck

