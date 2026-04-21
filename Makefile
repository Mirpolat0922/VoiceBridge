run:
	python -m voicebridge.main

test:
	pytest

lint:
	ruff check .
