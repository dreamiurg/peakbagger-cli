.PHONY: lint typecheck test coverage complexity check ci

lint:
	uv run ruff check peakbagger tests
	uv run ruff format --check peakbagger tests

typecheck:
	uvx ty check peakbagger

test:
	uv run pytest --no-header -q

coverage:
	uv run pytest --cov=peakbagger --cov-report=term-missing --cov-report=html --cov-fail-under=85

complexity:
	lizard -l python -C 15 -L 60 -a 5 -w -x 'test_*.py' -x '*_test.py' -x '*/cli.py' peakbagger/

check: lint typecheck complexity
ci: check coverage
