from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RefreshTokenRequest,
    ChangePasswordRequest
)
from app.services.auth_service import AuthService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

#Đăng ký tài khoản (Register – Multi-tenant)
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register new user"
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register user into a tenant.
    Roles: Admin, PM, Contributor, Customer
    """
    try:
        AuthService.register(db, payload)
        return {
            "success": True,
            "message": "User registered successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
#Đăng nhập (Login – JWT)
@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login and get JWT tokens"
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login using email, password and tenant code.
    Used by Web & Mobile.
    """
    tokens = AuthService.login(db, payload)

    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email, password or tenant"
        )

    return tokens
#Refresh Access Token
@router.post(
    "/refresh",
    response_model=LoginResponse,
    summary="Refresh access token"
)
def refresh_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh JWT token without re-login.
    """
    try:
        return AuthService.refresh_token(db, payload.refresh_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
#Đăng xuất (Logout)
@router.post(
    "/logout",
    summary="Logout"
)
def logout(
    current_user: User = Depends(get_current_user)
):
    """
    JWT is stateless → client removes token.
    Endpoint used for audit logging.
    """
    return {
        "success": True,
        "message": "Logout successful"
    }
#Lấy thông tin người dùng hiện tại (/me)
@router.get(
    "/me",
    summary="Get current user profile"
)
def get_current_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Used by dashboard (Admin, PM, Contributor, Customer).
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.name if current_user.role else None,
        "tenant_id": current_user.tenant_id,
        "is_active": current_user.is_active
    }
#Đổi mật khẩu
@router.post(
    "/change-password",
    summary="Change password"
)
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Allow user to change their password.
    """
    try:
        AuthService.change_password(
            db=db,
            user=current_user,
            old_password=payload.old_password,
            new_password=payload.new_password
        )
        return {
            "success": True,
            "message": "Password changed successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
#Kiểm tra quyền truy cập (RBAC – dùng cho FE)
@router.get(
    "/check-permission",
    summary="Check user permission"
)
def check_permission(
    permission: str,
    current_user: User = Depends(get_current_user)
):
    """
    Example:
    /auth/check-permission?permission=project:create
    """
    if not current_user.has_permission(permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    return {
        "success": True,
        "message": "Permission granted"
    }
