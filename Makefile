.PHONY: test main lint clean
main: lint-local test-local clean

lint: lint-local clean
lint-ci: lint-local
	@echo 'ci lint done.'
lint-local:
	flake8 --show-source --statistics --count

test: test-local clean
test-local:
	pytest --cov-report=term --cov-report=xml --cov=src -n=5 test
	@echo 'test done.'

clean: clean-pytest clean-python
	@echo 'clean done.'
clean-pytest:
	rm -rf .coverage.*
	# rm -rf coverage.xml
	find . -name '.pytest_cache' | xargs rm -r
	find . -name '.coverage' | xargs rm -r
clean-python:
	find . -name '__pycache__' | xargs rm -r
