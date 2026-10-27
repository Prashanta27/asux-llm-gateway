FROM python:3.11-slim as builder

# Setup environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Install python dependencies in a virtualenv
COPY pyproject.toml README.md ./
RUN pip install hatchling && \
    python -m venv /opt/venv && \
    /opt/venv/bin/pip install -e .

# Final stage
FROM python:3.11-slim

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv
COPY src /app/src
COPY pyproject.toml README.md /app/

# Create a non-root user
RUN useradd -m asux && chown -R asux:asux /app
USER asux

EXPOSE 8000

CMD ["python", "-m", "asux_llm_gateway.__main__"]
