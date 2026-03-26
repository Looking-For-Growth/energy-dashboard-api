FROM python:3.11-alpine

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip --no-cache-dir \
    && pip install poetry --no-cache-dir \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --without dev \
    && pip uninstall -y poetry

COPY api .

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
