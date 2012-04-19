.PHONY: help docs arch test

SHELL ?= /bin/sh

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
	cram --shell="$(SHELL)" tests/*.t

coverage:
	coverage run -a opster.py
	COVERAGE=1 cram --shell="$(SHELL)" tests/*.t

upload:
	python setup.py sdist upload
