from pydantic import BaseModel, EmailStr, Field
from typing import Optional
#Schema đăng nhập
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="user@gmail.com")
    password: str = Field(..., min_length=6, example="123456")
    tenant_code: str = Field(..., example="company_a")
#Response sau khi đăng nhập / refresh token
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
#Schema đăng ký người dùng (Multi-tenant)
class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., example="newuser@gmail.com")
    password: str = Field(..., min_length=6, example="123456")
    full_name: str = Field(..., example="Nguyen Van A")
    role: str = Field(..., example="Contributor")
    tenant_id: int = Field(..., example=1)
#Refresh token
class RefreshTokenRequest(BaseModel):
    refresh_token: str
#Đổi mật khẩu
class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., example="oldpassword")
    new_password: str = Field(..., min_length=6, example="newpassword")
#Schema response thông tin user
class UserProfileResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: Optional[str]
    tenant_id: int
    is_active: bool
