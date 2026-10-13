from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import Base, engine, SessionLocal
from app.database.seed import seed_if_empty
from app.database import models
from app.api import materials, matches, requests, businesses, impact, auth

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_if_empty(db)

app = FastAPI(title="ScrapSync API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(materials.router, prefix="/api")
app.include_router(matches.router, prefix="/api")
app.include_router(requests.router, prefix="/api")
app.include_router(businesses.router, prefix="/api")
app.include_router(impact.router, prefix="/api")
app.include_router(auth.router, prefix="/api")

@app.get("/api/health")
def health():
    return {"status":"ok","service":"ScrapSync API"}

@app.post("/api/seed")
def seed():
    from app.database.seed import force_seed
    with SessionLocal() as db:
        force_seed(db)
    return {"status":"ok","message":"Demo network loaded"}