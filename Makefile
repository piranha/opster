.PHONY: help docs arch test

SHELL ?= /bin/sh
PRYSK = prysk --shell="$(SHELL)" --preserve-env
BUILD_DIR = `pwd`/build/lib
PYTHON = python3
VERSION = $(shell grep '__version__ =' opster.py | cut -d ' ' -f 3 | tr -d "'")

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
	$(PYTHON) contrib/updatepkg.py

test:
	$(PYTHON) opster.py
	$(PRYSK) tests/opster.t
	$(PRYSK) tests/py3k.t

coverage:
	coverage run -a opster.py
	COVERAGE=1 $(PRYSK) tests/opster.t

upload:
	python3 setup.py sdist
	twine upload dist/opster-$(VERSION).tar.gz
