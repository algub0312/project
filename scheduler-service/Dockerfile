FROM astral/uv:python3.13-bookworm-slim
WORKDIR /app

COPY pyproject.toml alembic.ini uv.lock .env .python-version main.py README.md ./
COPY src ./src
COPY migrations ./migrations
RUN uv venv && uv sync

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0"]