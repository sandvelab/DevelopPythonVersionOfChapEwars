# R-INLA is amd64-only.
ARG BASE_PLATFORM=linux/amd64

FROM --platform=${BASE_PLATFORM} ghcr.io/dhis2-chap/chapkit-r-inla:latest

ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# Build steps run as root; the service runs as the unprivileged chapkit user (uid/gid 1000).
# Newer chapkit base images ship the user, older ones do not, so create it only when missing.
USER root
RUN id -u chapkit >/dev/null 2>&1 \
    || (groupadd --gid 1000 chapkit && useradd --uid 1000 --gid 1000 --no-create-home --shell /usr/sbin/nologin chapkit)

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Commit the image was built from, reported as git_revision on /api/v1/info.
# The publish workflow passes it; locally: --build-arg GIT_REVISION=$(git rev-parse HEAD)
ARG GIT_REVISION=""
ENV GIT_REVISION=${GIT_REVISION}

COPY main.py ./
COPY scripts/ ./scripts/

# INLA's binaries in the base image are executable by root only; open the R library up
# so the unprivileged user can run them (chapkit-images will ship this fix, harmless after).
RUN chmod -R a+rX /usr/local/lib/R/site-library

# Writable paths at runtime are /app/data (SQLite, a volume in compose.yml) and /tmp
# (ML workspaces, a tmpfs in compose.yml); everything else stays read-only.
RUN mkdir -p /app/data && chown -R chapkit:chapkit /app/data
ENV HOME=/tmp \
    MPLCONFIGDIR=/tmp \
    XDG_CACHE_HOME=/tmp/.cache
USER chapkit

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
