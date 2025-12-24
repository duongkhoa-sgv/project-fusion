from fastapi import APIRouter, Depends, HTTPException
from app.schemas.sprint import (
    SprintCreate,
    SprintUpdate,
    SprintResponse
)
from app.services.sprint_service import SprintService
from app.dependencies.auth import get_current_user
from app.dependencies.permission import require_role

router = APIRouter(prefix="/sprints", tags=["Sprints"])


# 1. Tạo sprint (PM / Leader)
@router.post("/", response_model=SprintResponse)
def create_sprint(
    data: SprintCreate,
    user=Depends(require_role("PM", "LEADER"))
):
    return SprintService.create_sprint(data, user)


# 2. Danh sách sprint theo project
@router.get("/project/{project_id}", response_model=list[SprintResponse])
def list_sprints_by_project(
    project_id: int,
    user=Depends(get_current_user)
):
    return SprintService.get_by_project(project_id, user)


# 3. Chi tiết sprint
@router.get("/{sprint_id}", response_model=SprintResponse)
def sprint_detail(
    sprint_id: int,
    user=Depends(get_current_user)
):
    sprint = SprintService.get_detail(sprint_id, user)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return sprint


# 4. Cập nhật sprint (chỉ khi chưa start)
@router.put("/{sprint_id}", response_model=SprintResponse)
def update_sprint(
    sprint_id: int,
    data: SprintUpdate,
    user=Depends(require_role("PM", "LEADER"))
):
    return SprintService.update_sprint(sprint_id, data, user)


# 5. Start sprint
@router.post("/{sprint_id}/start")
def start_sprint(
    sprint_id: int,
    user=Depends(require_role("PM", "LEADER"))
):
    SprintService.start_sprint(sprint_id, user)
    return {
        "message": "Sprint started successfully"
    }


# 6. Close sprint
@router.post("/{sprint_id}/close")
def close_sprint(
    sprint_id: int,
    user=Depends(require_role("PM", "LEADER"))
):
    SprintService.close_sprint(sprint_id, user)
    return {
        "message": "Sprint closed successfully"
    }


# 7. Gán task vào sprint
@router.post("/{sprint_id}/assign-task/{task_id}")
def assign_task_to_sprint(
    sprint_id: int,
    task_id: int,
    user=Depends(require_role("PM", "LEADER"))
):
    SprintService.assign_task(sprint_id, task_id, user)
    return {
        "message": "Task assigned to sprint successfully"
    }


# 8. Danh sách task trong sprint
@router.get("/{sprint_id}/tasks")
def get_tasks_in_sprint(
    sprint_id: int,
    user=Depends(get_current_user)
):
    return SprintService.get_tasks(sprint_id, user)
