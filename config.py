"""Configurazione server — legge da variabili d'ambiente / .env"""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./eduland_dev.db")
JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-fallback-secret-change-me")
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRY_DAYS: int = 30

# Render.com fornisce DATABASE_URL con "postgres://" ma SQLAlchemy vuole "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
