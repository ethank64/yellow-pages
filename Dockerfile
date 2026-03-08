# YellowPages MCP server - run with streamable-http for Docker
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application and schema
COPY main.py ./
COPY src ./src
COPY sample_schema.json ./

# Default: run MCP with streamable-http (port 8000)
ENV YELLOW_PAGES_TRANSPORT=streamable-http
EXPOSE 8000
ENTRYPOINT ["uv", "run", "python", "-m", "src.server"]
