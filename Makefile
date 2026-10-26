PYTHON ?= python3
CONFIG ?= config.yaml

.PHONY: install run test

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	PYTHONPATH=src $(PYTHON) -m depviz $(CONFIG)

test:
	$(PYTHON) -m pytest -v
