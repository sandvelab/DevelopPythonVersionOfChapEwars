# Python 3.13 with uv, pinned by digest. No R and no INLA, so the image builds and runs
# natively on amd64 and arm64 alike (the R original needs amd64 emulation on Apple Silicon).
FROM ghcr.io/astral-sh/uv:0.8.22-python3.13-bookworm-slim@sha256:c4a67221d74ad160ddf4e114804bda0f8dd2d2e1aa5c16e0817cf8530ff8f5f6

ENV UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_COMPILE_BYTECODE=1 \
    PATH="/app/.venv/bin:${PATH}"

# git fetches dlnmpy at its pinned commit; curl serves the health check.
RUN apt-get update && apt-get install -y --no-install-recommends git curl \
    && rm -rf /var/lib/apt/lists/*
RUN groupadd --gid 1000 chapkit && useradd --uid 1000 --gid 1000 --no-create-home --shell /usr/sbin/nologin chapkit

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY main.py ./
COPY scripts/ ./scripts/
COPY ewars_python/ ./ewars_python/

# Writable paths at runtime are /app/data (SQLite) and /tmp (chapkit's ML workspaces).
RUN mkdir -p /app/data && chown -R chapkit:chapkit /app/data
ENV HOME=/tmp XDG_CACHE_HOME=/tmp/.cache
USER chapkit

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
