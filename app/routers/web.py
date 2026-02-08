from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Phase, Priority
from app.schemas import TodoCreate, TodoUpdate, SkillResponse
from app.services.todo_service import TodoService
from app.config import PHASE_SKILLS, get_skills_for_phase

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/templates")

PHASES = [p.value for p in Phase]
PRIORITIES = [p.value for p in Priority]


def get_todo_service(db: Session = Depends(get_db)) -> TodoService:
    return TodoService(db)


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, service: TodoService = Depends(get_todo_service)):
    todos = service.list()
    todos_by_phase = {phase: [] for phase in PHASES}
    for todo in todos:
        todos_by_phase[todo.phase.value].append(todo)

    skills_by_phase = {
        phase: [s for s in PHASE_SKILLS.get(phase, [])] for phase in PHASES
    }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "phases": PHASES,
            "todos_by_phase": todos_by_phase,
            "skills_by_phase": skills_by_phase,
        },
    )


@router.get("/todos", response_class=HTMLResponse)
def list_todos(
    request: Request,
    phase: Optional[str] = None,
    priority: Optional[str] = None,
    completed: Optional[str] = None,
    service: TodoService = Depends(get_todo_service),
):
    phase_enum = Phase(phase) if phase else None
    priority_enum = Priority(priority) if priority else None
    completed_bool = None
    if completed == "true":
        completed_bool = True
    elif completed == "false":
        completed_bool = False

    todos = service.list(phase=phase_enum, priority=priority_enum, completed=completed_bool)

    return templates.TemplateResponse(
        "todos/list.html",
        {
            "request": request,
            "todos": todos,
            "phases": PHASES,
            "priorities": PRIORITIES,
            "phase": phase,
            "priority": priority,
            "completed": completed,
        },
    )


@router.get("/todos/new", response_class=HTMLResponse)
def new_todo_form(request: Request):
    return templates.TemplateResponse(
        "todos/form.html",
        {
            "request": request,
            "todo": None,
            "phases": PHASES,
            "priorities": PRIORITIES,
        },
    )


@router.post("/todos/new")
def create_todo(
    title: str = Form(...),
    description: str = Form(""),
    phase: str = Form(...),
    priority: str = Form(...),
    due_date: str = Form(""),
    service: TodoService = Depends(get_todo_service),
):
    parsed_date = None
    if due_date:
        parsed_date = date.fromisoformat(due_date)

    data = TodoCreate(
        title=title,
        description=description if description else None,
        phase=Phase(phase),
        priority=Priority(priority),
        due_date=parsed_date,
    )
    todo = service.create(data)
    return RedirectResponse(url=f"/todos/{todo.id}", status_code=303)


@router.get("/todos/{todo_id}", response_class=HTMLResponse)
def todo_detail(
    request: Request,
    todo_id: int,
    service: TodoService = Depends(get_todo_service),
):
    todo = service.get(todo_id)
    if not todo:
        return RedirectResponse(url="/todos", status_code=303)

    skills = get_skills_for_phase(todo.phase.value)
    skill_responses = [SkillResponse(**s) for s in skills]

    return templates.TemplateResponse(
        "todos/detail.html",
        {
            "request": request,
            "todo": todo,
            "recommended_skills": skill_responses,
        },
    )


@router.get("/todos/{todo_id}/edit", response_class=HTMLResponse)
def edit_todo_form(
    request: Request,
    todo_id: int,
    service: TodoService = Depends(get_todo_service),
):
    todo = service.get(todo_id)
    if not todo:
        return RedirectResponse(url="/todos", status_code=303)

    return templates.TemplateResponse(
        "todos/form.html",
        {
            "request": request,
            "todo": todo,
            "phases": PHASES,
            "priorities": PRIORITIES,
        },
    )


@router.post("/todos/{todo_id}/edit")
def update_todo(
    todo_id: int,
    title: str = Form(...),
    description: str = Form(""),
    phase: str = Form(...),
    priority: str = Form(...),
    due_date: str = Form(""),
    service: TodoService = Depends(get_todo_service),
):
    parsed_date = None
    if due_date:
        parsed_date = date.fromisoformat(due_date)

    data = TodoUpdate(
        title=title,
        description=description if description else None,
        phase=Phase(phase),
        priority=Priority(priority),
        due_date=parsed_date,
    )
    service.update(todo_id, data)
    return RedirectResponse(url=f"/todos/{todo_id}", status_code=303)


@router.post("/todos/{todo_id}/toggle")
def toggle_complete(
    todo_id: int,
    service: TodoService = Depends(get_todo_service),
):
    service.toggle_complete(todo_id)
    return RedirectResponse(url=f"/todos/{todo_id}", status_code=303)


@router.post("/todos/{todo_id}/delete")
def delete_todo(
    todo_id: int,
    service: TodoService = Depends(get_todo_service),
):
    service.delete(todo_id)
    return RedirectResponse(url="/", status_code=303)


@router.get("/phases", response_class=HTMLResponse)
def list_phases(request: Request):
    phases = []
    for phase_name in PHASE_SKILLS.keys():
        skills = get_skills_for_phase(phase_name)
        phases.append({
            "name": phase_name,
            "skills": [SkillResponse(**s) for s in skills],
        })

    return templates.TemplateResponse(
        "phases.html",
        {
            "request": request,
            "phases": phases,
        },
    )
