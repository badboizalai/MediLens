# Worker image with the `ocr` extra (PaddleOCR, VietOCR, OpenCV, CPU-only torch).
# Build: docker build -t medilens-worker apps/worker
# Build stage: tooling (uv, pip, setuptools, wheel) stays here and is not shipped.
FROM python:3.10-slim AS build
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip setuptools wheel uv
COPY pyproject.toml README.md ./
COPY src ./src
# CPU wheels for torch (no CUDA, saves ~2 GB); other packages still resolve from PyPI.
RUN uv venv /opt/venv && uv pip install --python /opt/venv/bin/python --no-cache \
    --extra-index-url https://download.pytorch.org/whl/cpu --index-strategy unsafe-best-match \
    ".[ocr]"

# Runtime stage: only the venv; pip/setuptools/wheel removed from the base image.
FROM python:3.10-slim
# libgomp1: OpenMP runtime needed by paddle/torch wheels.
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && pip uninstall -y setuptools wheel pip 2>/dev/null || true
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1
WORKDIR /app
USER 10001
CMD ["python", "-m", "medilens_worker.main"]
