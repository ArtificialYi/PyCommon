.PHONY: test main lint clean
main: lint-local test-local clean

lint: lint-local clean
lint-ci: lint-local
	@echo 'ci lint done.'
lint-local:
	flake8 --show-source --statistics --count

test: test-local clean
test-local:
	pytest --cov-report=term --cov-report=xml --cov=src -n=6 test
	@echo 'test done.'

clean: clean-pytest clean-python
	@echo 'clean done.'
clean-pytest:
	find . -name .coverage.* -exec rm -rf {} +
	find . -name .pytest_cache -exec rm -r {} +
	find . -name .coverage -exec rm -r {} +
clean-python:
	find . -name __pycache__ -exec rm -r {} +
