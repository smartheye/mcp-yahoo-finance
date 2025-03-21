FROM python:3.13-alpine
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
RUN uv sync --frozen

# 执行命令 uv run main --transport sse
CMD ["uv", "run", "main", "--transport", "sse"]