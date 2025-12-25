from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# =====================================================
# Base schema dùng chung
# =====================================================
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True


# region 1. Schema tạo user
# Dùng cho: POST /users
class UserCreate(UserBase):
    password: str
    tenant_id: int
    role_id: int
# endregion


# region 2. Schema cập nhật user
# Dùng cho: PUT /users/{id}
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
# endregion


# region 3. Schema đổi mật khẩu user
# Dùng cho: PUT /users/{id}/password
class UserChangePassword(BaseModel):
    new_password: str
# endregion


# region 4. Schema response user
# Dùng cho: tất cả API trả user
class UserResponse(UserBase):
    id: int
    tenant_id: int
    role_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
# endregion
// test commit by me