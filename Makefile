run:
	uv run --env-file dev.env uvicorn app.main:app --reload

test:
	uv run --env-file test.env pytest tests -s
