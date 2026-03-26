export APP_DEBUG=true
export APP_DEVELOPMENT=true
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
