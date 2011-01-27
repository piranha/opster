.PHONY: help docs arch

help:
	@echo "Use \`make <target>\` with one of targets:"
	@echo "  docs  build docs"
	@echo "  arch  update archlinux pkgbuild"

docs:
	cd docs && make

arch:
	python contrib/updatepkg.py
