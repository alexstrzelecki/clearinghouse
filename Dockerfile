# Install uv
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.6.9 /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install third party dependencies without clearinghouse
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

COPY ./clearinghouse /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

# Set default Schwab dependency variables
ENV SCHWAB_USE_DEFAULT_TRADING_ACCOUNT=True
ENV SCHWAB_LOCAL_MODE=True
ENV SCHWAB_READ_ONLY_MODE=False

ENV DEV_MODE=False

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
