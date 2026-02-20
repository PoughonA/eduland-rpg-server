"""EdulandRPG — Server API principale.
Avvio: uvicorn main:app --reload --port 8080
Deploy: Render.com (vedi render.yaml)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes_auth import router as auth_router
from routes_characters import router as characters_router
from routes_progress import router as progress_router
from routes_community import router as community_router

# Crea tabelle automaticamente all'avvio
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EdulandRPG API",
    description="Backend per il gioco educativo Eduland RPG — Scrapyard Scholars",
    version="1.0.0",
)

# CORS — permetti richieste da qualsiasi origine (necessario per Godot su Android)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra tutti i router
app.include_router(auth_router)
app.include_router(characters_router)
app.include_router(progress_router)
app.include_router(community_router)


@app.get("/")
def root():
    return {
        "name": "EdulandRPG API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
