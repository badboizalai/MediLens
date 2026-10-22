FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml ./
COPY src ./src
RUN uv pip install --system --no-cache .
USER 10001
CMD ["uvicorn", "medilens.main:app", "--host", "0.0.0.0", "--port", "8000"]
