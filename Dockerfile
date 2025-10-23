FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen --no-cache

COPY main.py .
COPY commands/ ./commands/

EXPOSE 10000

CMD ["uv", "run", "fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "10000"]