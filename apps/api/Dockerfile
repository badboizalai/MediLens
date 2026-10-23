# Build stage: tooling (uv, pip, setuptools, wheel) stays here and is not shipped.
FROM python:3.10-slim AS build
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip setuptools wheel uv
COPY pyproject.toml ./
COPY src ./src
RUN uv venv /opt/venv && uv pip install --python /opt/venv/bin/python --no-cache .

# Runtime stage: only the venv; pip/setuptools/wheel removed from the base image.
FROM python:3.10-slim
RUN pip uninstall -y setuptools wheel pip 2>/dev/null || true
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
USER 10001
CMD ["uvicorn", "medilens.main:app", "--host", "0.0.0.0", "--port", "8000"]
