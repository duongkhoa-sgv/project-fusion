from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut, ProjectMemberAssignment
from app.schemas.common import Message
from app.services import project_service, ai_service
from app.core.security import get_current_user, PermissionChecker
from app.core.tenant_context import get_current_tenant_id
from app.models.user import User

router = APIRouter(prefix="/projects", tags=["Projects"])

# --- Quản lý Dự án Nội bộ (Internal Projects) ---

@router.get("/", response_model=List[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user)
):
    """Lấy danh sách dự án thuộc Tenant hiện tại."""
    return project_service.get_multi_by_tenant(db, tenant_id=tenant_id, user_id=current_user.id)

@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    # Chỉ PM hoặc Tenant Admin mới có quyền tạo
    _ = Depends(PermissionChecker(["project:create"])) 
):
    """Tạo dự án mới trong không gian làm việc của Tenant."""
    return project_service.create_with_tenant(db, obj_in=project_in, tenant_id=tenant_id, owner_id=current_user.id)

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    _ = Depends(PermissionChecker(["project:view"]))
):
    """Xem chi tiết một dự án cụ thể."""
    project = project_service.get_by_id(db, id=project_id, tenant_id=tenant_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    _ = Depends(PermissionChecker(["project:edit"]))
):
    """Cập nhật thông tin dự án."""
    return project_service.update_project(db, id=project_id, obj_in=project_in, tenant_id=tenant_id)

# --- Quản lý Thành viên & Phân quyền dự án ---

@router.post("/{project_id}/members", response_model=Message)
def assign_member(
    project_id: int,
    assignment: ProjectMemberAssignment,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    _ = Depends(PermissionChecker(["project:manage_members"]))
):
    """Gán thành viên (Dev, QA, BA) vào dự án với Role cụ thể."""
    success = project_service.add_member_to_project(db, project_id, assignment, tenant_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not assign member")
    return {"message": "Member assigned successfully"}

# --- Tính năng AI thông minh ---

@router.post("/{project_id}/generate-roadmap")
async def generate_ai_roadmap(
    project_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    _ = Depends(PermissionChecker(["project:edit"]))
):
    """Sử dụng AI để tự động tạo lộ trình (Roadmap) dựa trên feedback và tài liệu."""
    project = project_service.get_by_id(db, id=project_id, tenant_id=tenant_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Chạy xử lý AI dưới nền để tránh blocking API
    background_tasks.add_task(ai_service.generate_project_roadmap, db, project_id)
    return {"message": "AI Roadmap generation started in background"}

# --- Hợp tác liên doanh nghiệp (Inter-Company Partnership) ---

@router.post("/requests", response_model=Message)
def send_project_request(
    target_tenant_id: str,
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    source_tenant_id: str = Depends(get_current_tenant_id),
    _ = Depends(PermissionChecker(["partnership:request"]))
):
    """Gửi yêu cầu thuê dự án cho một công ty đối tác (Partnership)."""
    # Kiểm tra xem 2 công ty đã ký kết Partnership chưa
    if not project_service.check_partnership(db, source_tenant_id, target_tenant_id):
        raise HTTPException(status_code=403, detail="No active partnership with this company")
    
    project_service.create_partnership_request(db, source_tenant_id, target_tenant_id, project_data)
    return {"message": "Project request sent to partner"}