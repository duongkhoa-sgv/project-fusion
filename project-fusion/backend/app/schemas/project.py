from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

# --- Enums cho Project ---

class ProjectStatus(str, Enum):
    PROPOSAL = "proposal"       # Giai đoạn đề xuất/thương thảo
    ACTIVE = "active"           # Đang thực hiện
    MAINTENANCE = "maintenance" # Giai đoạn bảo trì
    COMPLETED = "completed"     # Đã hoàn thành
    ON_HOLD = "on_hold"         # Đang tạm dừng

class ProjectType(str, Enum):
    INTERNAL = "internal"       # Dự án nội bộ của Tenant
    OUTSOURCED = "outsourced"   # Dự án thuê ngoài (từ đối tác)

# --- Member Schemas ---

class ProjectMemberBase(BaseModel):
    user_id: int
    role_id: int  # Tham chiếu đến Role nội bộ của Tenant (PM, Dev, QA, etc.)

class ProjectMemberAssignment(ProjectMemberBase):
    """Dùng khi gán thành viên vào dự án"""
    pass

class ProjectMemberOut(ProjectMemberBase):
    """Dùng khi hiển thị thông tin thành viên dự án"""
    full_name: str
    email: str
    role_name: str # Tên role (ví dụ: Senior Developer)

    model_config = ConfigDict(from_attributes=True)

# --- Project Schemas ---

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, example="Hệ thống CRM FUSION")
    description: Optional[str] = Field(None, example="Dự án phát triển hệ thống quản lý khách hàng")
    project_type: ProjectType = ProjectType.INTERNAL
    status: ProjectStatus = ProjectStatus.PROPOSAL

class ProjectCreate(ProjectBase):
    """Dữ liệu khi tạo dự án mới"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    # Đối với Project Request giữa các công ty:
    budget: Optional[float] = Field(None, description="Ngân sách dự kiến nếu là dự án hợp tác")

class ProjectUpdate(BaseModel):
    """Dữ liệu khi cập nhật dự án (tất cả các trường là Optional)"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    end_date: Optional[datetime] = None
    priority: Optional[int] = Field(None, ge=1, le=5)

class ProjectOut(ProjectBase):
    """Dữ liệu trả về cho Client"""
    id: int
    tenant_id: str
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    # Danh sách thành viên tham gia
    members: List[ProjectMemberOut] = []
    
    # Metadata bổ sung (có thể dùng cho AI Roadmap)
    completion_percentage: float = 0.0

    model_config = ConfigDict(from_attributes=True)

# --- Partnership Request Schemas ---

class ProjectRequestOut(ProjectOut):
    """Dùng cho luồng Inter-Company Partnership"""
    source_tenant_id: str  # Công ty gửi yêu cầu (Khách hàng)
    target_tenant_id: str  # Công ty nhận yêu cầu (Nhà thầu)
    is_accepted: bool = False