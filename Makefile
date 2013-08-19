.PHONY: help docs arch test

SHELL ?= /bin/sh
CRAM = cram --shell="$(SHELL)" --preserve-env
BUILD_DIR = `pwd`/build/lib
PYVER = $(shell python -V 2>&1 | cut -c8)

ifeq ($(PYVER), 2)
PYTHON3 = python3
else
PYTHON3 = python
endif

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
	$(CRAM) tests/opster.t

test3:
	"$(PYTHON3)" setup.py build
	2to3 --doctests_only --write "$(BUILD_DIR)"/opster.py
	"$(PYTHON3)" "$(BUILD_DIR)"/opster.py
	PYTHON="$(PYTHON3)" OPSTER_DIR="$(BUILD_DIR)" $(CRAM) tests/opster.t
	PYTHON="$(PYTHON3)" OPSTER_DIR="$(BUILD_DIR)" $(CRAM) tests/py3k.t

ifeq ($(PYVER), 2)
testcurrent: test
else
testcurrent: test3
endif

coverage:
	coverage run -a opster.py
	COVERAGE=1 $(CRAM) tests/opster.t

upload:
	python setup.py sdist upload
