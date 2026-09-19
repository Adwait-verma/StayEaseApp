import os
from typing import ClassVar


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://stayease:stayease-local-password@localhost:3306/stayease",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS: ClassVar[dict] = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }
    JWT_SECRET = os.getenv("JWT_SECRET", "development-only-secret-change-me")
    JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES", "120"))
    JSON_SORT_KEYS = False
