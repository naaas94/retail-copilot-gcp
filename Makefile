.PHONY: install test run eval docker-build docker-run

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/

run:
	streamlit run src/ui/app.py

eval:
	python scripts/evaluate_golden_set.py

docker-build:
	docker build -t retail-copilot .

docker-run:
	docker-compose up
