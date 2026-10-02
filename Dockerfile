FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /uvx /bin/

WORKDIR /app

# Install dependencies before copying the code so code edits reuse this layer.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-cache

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "website.main:app", "--host", "0.0.0.0", "--port", "8000"]
