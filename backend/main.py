from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import dashboard  # Import dashboard router

app = FastAPI(title="Fusion Backend API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include dashboard router
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

# Root endpoint
@app.get("/")
def root():
    return {
        "status": "Backend running",
        "framework": "FastAPI"
    }