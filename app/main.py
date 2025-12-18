from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, invoices, compliance, audit
from app.db.session import engine
from app.db.models import Base
from app.core.logging import setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables (For production, use Alembic)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not connect to database on startup: {e}")
    yield

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME, 
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(invoices.router, prefix=f"{settings.API_V1_STR}/invoices", tags=["invoices"])
app.include_router(compliance.router, prefix=f"{settings.API_V1_STR}/compliance", tags=["compliance"])
app.include_router(audit.router, prefix=f"{settings.API_V1_STR}/audit", tags=["audit"])

@app.get("/")
def health_check():
    return {"status": "ok", "service": "GST Compliance Backend"}
