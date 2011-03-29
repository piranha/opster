.PHONY: help docs arch

help:
	@echo "Use \`make <target>\` with one of targets:"
	@echo "  docs  build docs"
	@echo "  open  open docs"
	@echo "  arch  update archlinux pkgbuild"

docs:
	cd docs && make

open:
	cd docs && make open

arch:
	python contrib/updatepkg.py
