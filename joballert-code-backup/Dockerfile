FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# install package + runtime deps from pyproject
COPY pyproject.toml README.md ./
COPY src ./src
COPY automation ./automation

RUN pip install --upgrade pip && pip install .

EXPOSE 8000

CMD ["uvicorn", "automation.microsaas.search_api:app", "--host", "0.0.0.0", "--port", "8000"]
