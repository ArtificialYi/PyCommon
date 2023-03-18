.PHONY: test
main: lint-local test-local clean

lint: lint-local clean
lint-ci: lint-local
	@echo 'ci lint done.'
lint-local:
	flake8 --show-source --statistics --count

test: test-local clean
test-local:
	pytest
	@echo 'test done.'
test-ci:
	pytest --cov-report=xml

clean: clean-pytest clean-python
	@echo 'clean done.'
clean-pytest:
	rm -rf coverage.xml .coverage .pytest_cache .coverage.*
clean-python:
	find . -name '__pycache__' | xargs rm -r
