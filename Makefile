.PHONY: help docs arch test

SHELL ?= /bin/sh
CRAM = cram --shell="$(SHELL)"
PYTHON3 = python3
BUILD_DIR = `pwd`/build/lib

help:
	@echo "Use \`make <target>\` with one of targets:"
	@echo "  docs  build docs"
	@echo "  open  open docs"
	@echo "  arch  update archlinux pkgbuild"
	@echo "  test  run tests"

docs:
	cd docs && make

open:
	cd docs && make open

arch:
	python contrib/updatepkg.py

test:
	python opster.py
	$(CRAM) tests/*.t

test2to3:
	"$(PYTHON3)" setup.py build
	2to3 --doctests_only --write "$(BUILD_DIR)"/opster.py
	"$(PYTHON3)" "$(BUILD_DIR)"/opster.py
	PYTHON="$(PYTHON3)" OPSTER_DIR="$(BUILD_DIR)" $(CRAM) tests/*.t

coverage:
	coverage run -a opster.py
	COVERAGE=1 $(CRAM) tests/*.t

upload:
	python setup.py sdist upload
