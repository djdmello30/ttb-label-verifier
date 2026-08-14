from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.labels import router as labels_router


app = FastAPI(
    title="TTB Alcohol Label Verification API",
    description="AI-powered alcohol beverage label verification system",
    version="0.1.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Basic Routes
# =========================================================

@app.get("/")
def root():
    return {
        "message": "TTB Alcohol Label Verification API",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# =========================================================
# Label Routes
# =========================================================

app.include_router(labels_router)