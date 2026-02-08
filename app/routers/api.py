from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Phase, Priority
from app.schemas import (
    TodoCreate,
    TodoUpdate,
    TodoResponse,
    PhaseResponse,
    SkillResponse,
)
from app.services.todo_service import TodoService
from app.config import PHASE_SKILLS, get_skills_for_phase

router = APIRouter(prefix="/api", tags=["api"])


def get_todo_service(db: Session = Depends(get_db)) -> TodoService:
    return TodoService(db)


@router.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(data: TodoCreate, service: TodoService = Depends(get_todo_service)):
    todo = service.create(data)
    return service.get_with_skills(todo.id)


@router.get("/todos", response_model=List[TodoResponse])
def list_todos(
    phase: Optional[Phase] = None,
    priority: Optional[Priority] = None,
    completed: Optional[bool] = None,
    service: TodoService = Depends(get_todo_service),
):
    todos = service.list(phase=phase, priority=priority, completed=completed)
    return [service.get_with_skills(todo.id) for todo in todos]


@router.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, service: TodoService = Depends(get_todo_service)):
    response = service.get_with_skills(todo_id)
    if not response:
        raise HTTPException(status_code=404, detail="Todo not found")
    return response


@router.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    data: TodoUpdate,
    service: TodoService = Depends(get_todo_service),
):
    todo = service.update(todo_id, data)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return service.get_with_skills(todo_id)


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, service: TodoService = Depends(get_todo_service)):
    if not service.delete(todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")
    return None


@router.patch("/todos/{todo_id}/complete", response_model=TodoResponse)
def toggle_complete(todo_id: int, service: TodoService = Depends(get_todo_service)):
    todo = service.toggle_complete(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return service.get_with_skills(todo_id)


@router.get("/phases", response_model=List[PhaseResponse])
def list_phases():
    phases = []
    for phase_name in PHASE_SKILLS.keys():
        skills = get_skills_for_phase(phase_name)
        phases.append(
            PhaseResponse(
                name=phase_name,
                skills=[SkillResponse(**s) for s in skills],
            )
        )
    return phases


@router.get("/phases/{phase_name}", response_model=PhaseResponse)
def get_phase(phase_name: str):
    if phase_name not in PHASE_SKILLS:
        raise HTTPException(status_code=404, detail="Phase not found")
    skills = get_skills_for_phase(phase_name)
    return PhaseResponse(
        name=phase_name,
        skills=[SkillResponse(**s) for s in skills],
    )
