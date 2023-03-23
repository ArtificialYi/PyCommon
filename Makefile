.PHONY: test
main: lint-local test-local clean

lint: lint-local clean
lint-ci: lint-local
	@echo 'ci lint done.'
lint-local:
	flake8 --show-source --statistics --count

test: test-local clean
test-local:
	pytest --cov-report=term --cov-report=xml
	@echo 'test done.'
test-ci:
	pytest

clean: clean-pytest clean-python
	@echo 'clean done.'
clean-pytest:
	rm -rf .coverage .pytest_cache .coverage.*
	# coverage.xml
clean-python:
	find . -name '__pycache__' | xargs rm -r
