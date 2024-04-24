.PHONY: build
build:
	python -m pylliterate

.PHONY: publish
publish:
	poetry publish --build

.PHONY: docs
docs:
	mkdocs gh-deploy

.PHONY: serve
serve:
	mkdocs serve
