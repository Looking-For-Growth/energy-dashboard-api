import os


DEVELOPMENT = os.environ.get("APP_DEVELOPMENT", "false").lower() == "true"

if DEVELOPMENT:
    SECRET_KEY = "dev-insecure-key"
else:
    SECRET_KEY = os.environ["APP_SECRET"]

DEBUG = DEVELOPMENT and os.environ.get("APP_DEBUG", "true").lower() != "false"

BMRS_API_KEY = os.environ.get("BMRS_API_KEY", None)

if DEVELOPMENT:
    CORS_ORIGINS = ["*"]
else:
    CORS_ORIGINS = [
        "https://energy.lookingforgrowth.uk",
        "https://energy.lfgdata.uk",
        "https://dashboards.lookingforgrowth.uk",
        "https://delays.lookingforgrowth.uk",
    ]
