install:
	poetry install

lint:
	poetry run pylint src/user_state_agent

run:
	poetry run python src/user_state_agent/agent.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
