.PHONY: clean-pyc clean-build docs generate-versions

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	rm -fr __pycache__/ .eggs/ .cache/ .tox/

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

generate-versions:
	python3 generate_versions.py

lint:
	uv run ruff check src 

format:
	uv run ruff format src

test:
	python -m pytest

build: generate-versions
	uv build

install: build
	uv pip install -e .

install-user: build
	uv pip install --user -e .

git:
	git push --all
	git push --tags

check:
	uv pip check

dev-setup:
	uv pip install --python-dev-deps -e .

dist: generate-versions
	uv build
	python -m twine upload dist/*

test-dist: generate-versions
	uv build
	python -m twine upload --repository testpypi dist/* --verbose

docs:
	# sphinx-apidoc -d 6 -e -f -o docs . *.py tests
	make -C docs clean html

release: clean check dist git
