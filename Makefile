.PHONY: run test

PYTHON ?= python3

run:
	PYTHONPATH=src $(PYTHON) -m shell_emulator $(ARGS)

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v
