.PHONY: install dev daemon test clean seed backtest lint

install:
	pip install -r requirements.txt

dev:
	uvicorn api.server:app --reload --port 8000

daemon:
	python core/daemon.py

test:
	pytest tests/ -v

lint:
	ruff check .
	black --check .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -f data/oracle.db
	rm -rf data/chroma

seed:
	python scripts/seed_memory.py

backtest:
	python scripts/backtest.py
