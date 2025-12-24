from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ===== Routers =====
from app.api import (
    auth,
    user,
    tenant,
    project,
    sprint,
    task,
    feedback,
    partnership,
    audit
)

# ===== Middleware =====
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.tenant_middleware import TenantMiddleware
from app.middleware.audit_middleware import AuditMiddleware

# ===== App init =====
app = FastAPI(
    title="FUSION Backend API",
    description="Multi-tenant Feedback-to-Delivery Platform",
    version="1.0.0"
)

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Khi deploy thì đổi lại domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Custom Middlewares =====
app.add_middleware(AuthMiddleware)
app.add_middleware(TenantMiddleware)
app.add_middleware(AuditMiddleware)

# ===== Register Routers =====
app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(tenant.router, prefix="/api")
app.include_router(project.router, prefix="/api")
app.include_router(sprint.router, prefix="/api")
app.include_router(task.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(partnership.router, prefix="/api")
app.include_router(audit.router, prefix="/api")

# ===== Health check =====
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "fusion-backend"
    }
