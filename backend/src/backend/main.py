from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.database import engine, Base, SessionLocal
from backend.models.models import Organization
from backend.demo.seed_data import reset_and_seed_db
from backend.demo.generate_demo_files import generate_all_excel_files
from backend.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist and run auto-migrations
    from backend.migrations import run_auto_migrations
    run_auto_migrations(engine)
    db = SessionLocal()
    try:
        org = db.query(Organization).first()
        if not org:
            print("Database empty: seeding Cafe Aroma demo data...")
            generate_all_excel_files()
            reset_and_seed_db(db)
            print("Cafe Aroma demo data successfully seeded.")
    finally:
        db.close()
    yield


app = FastAPI(
    title="BizMind API",
    description="Платформа финансовой аналитики и оптимизации закупок для малого бизнеса (Cafe Aroma MVP)",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "service": "BizMind Backend API",
        "status": "online",
        "version": "1.0.0",
        "demo_cases": [
            "Case A: Cafe Aroma (Initial Adoption / Migration)",
            "Case B: Daily Cup (Regular Usage / Growth)"
        ],
        "docs_url": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


def main():
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
