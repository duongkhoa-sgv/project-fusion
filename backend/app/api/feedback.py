from fastapi import APIRouter ,Depends , HTTPException ,status 
from sqlalchemy.orm import session 
from typing import List 

from app.db.session import get_db 
from app.core.security import get_current_user 
from app.core.tenant_context import get_current_tenant
from app.core.rbac import require_permission 

from app.schemas.feedback import(
    FeedbackCreate , 
    FeedbackUpdate , 
    FeedbackResponse , 
)
from app.services.feedback_service import FeedbackService
from app.models.user import User 

router = APIRouter(
    prefix = "/feedback" , 
    tags = ["Feedback"] 
)

# 1 . Create feedback (customer/BA/support)
@router.post (
    "" , 
    response_model = FeedbackResponse , 
    status_code = status.HTTP_201_CREATED
)
def create_feedback(
    payload: FeedbackCreate, 
    db:session = Depends(get_db) , 
    current_user : User = Depends(get_current_user), 
    teneant_id: int = Depends(get_current_tenant)
): 
    require_permission(current_user,"feedback:create")
    return FeedbackService.create_feedback (
        db = db , 
        tenant_id = teneant_id , 
        user_id = current_user.id , 
        data = payload
    )
# 2 .Get all feedback in current tenant 
@router.get("" , response_model= List[FeedbackResponse])
def get_feedback_list(
    db:session = Depends(get_db), 
    current_user:User = Depends(get_current_user), 
    tenant_id:int = Depends(get_current_tenant)

): 
    require_permission(get_current_user,"feedback:view")

    return FeedbackService.get_feedback_list(
        db=db , 
        tenant_id =tenant_id 
    )
# 3.Get feedback detail 
@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback_detail(
    feedback_id: int,
    db: session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    require_permission(current_user, "feedback:view")

    feedback = FeedbackService.get_feedback_by_id(
        db=db,
        tenant_id=tenant_id,
        feedback_id=feedback_id
    )

    if not feedback:
        raise HTTPException(
            status_code=404,
            detail="Feedback not found"
        )

    return feedback

# 4. Update feedback (BA / Support)
# =====================================================
@router.put("/{feedback_id}", response_model=FeedbackResponse)
def update_feedback(
    feedback_id: int,
    payload: FeedbackUpdate,
    db: session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    require_permission(current_user, "feedback:update")

    feedback = FeedbackService.update_feedback(
        db=db,
        tenant_id=tenant_id,
        feedback_id=feedback_id,
        data=payload
    )

    if not feedback:
        raise HTTPException(
            status_code=404,
            detail="Feedback not found"
        )

    return feedback

# 5. Convert feedback -> task (CORE FEATURE)

@router.post("/{feedback_id}/convert-to-task")
def convert_feedback_to_task(
    feedback_id: int,
    db: session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    require_permission(current_user, "task:create")

    task = FeedbackService.convert_to_task(
        db=db,
        tenant_id=tenant_id,
        feedback_id=feedback_id,
        user_id=current_user.id
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Feedback not found"
        )

    return {
        "message": "Feedback converted to task successfully",
        "task_id": task.id
    }
# 6. Delete feedback (PM / Admin)
@router.delete(
    "/{feedback_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_feedback(
    feedback_id: int,
    db: session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    require_permission(current_user, "feedback:delete")

    success = FeedbackService.delete_feedback(
        db=db,
        tenant_id=tenant_id,
        feedback_id=feedback_id
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Feedback not found"
        )

