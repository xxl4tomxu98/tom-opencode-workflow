from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Todo, Phase, Priority
from app.schemas import TodoCreate, TodoUpdate, TodoResponse, SkillResponse
from app.config import get_skills_for_phase


class TodoService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: TodoCreate) -> Todo:
        todo = Todo(
            title=data.title,
            description=data.description,
            phase=data.phase,
            priority=data.priority,
            due_date=data.due_date,
        )
        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def get(self, todo_id: int) -> Optional[Todo]:
        return self.db.query(Todo).filter(Todo.id == todo_id).first()

    def list(
        self,
        phase: Optional[Phase] = None,
        priority: Optional[Priority] = None,
        completed: Optional[bool] = None,
    ) -> List[Todo]:
        query = self.db.query(Todo)
        if phase is not None:
            query = query.filter(Todo.phase == phase)
        if priority is not None:
            query = query.filter(Todo.priority == priority)
        if completed is not None:
            query = query.filter(Todo.completed == completed)
        return query.order_by(Todo.created_at.desc()).all()

    def update(self, todo_id: int, data: TodoUpdate) -> Optional[Todo]:
        todo = self.get(todo_id)
        if not todo:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo, field, value)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def delete(self, todo_id: int) -> bool:
        todo = self.get(todo_id)
        if not todo:
            return False
        self.db.delete(todo)
        self.db.commit()
        return True

    def toggle_complete(self, todo_id: int) -> Optional[Todo]:
        todo = self.get(todo_id)
        if not todo:
            return None
        todo.completed = not todo.completed
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def get_with_skills(self, todo_id: int) -> Optional[TodoResponse]:
        todo = self.get(todo_id)
        if not todo:
            return None
        skills = get_skills_for_phase(todo.phase.value)
        skill_responses = [SkillResponse(**skill) for skill in skills]
        return TodoResponse(
            id=todo.id,
            title=todo.title,
            description=todo.description,
            phase=todo.phase,
            priority=todo.priority,
            due_date=todo.due_date,
            completed=todo.completed,
            created_at=todo.created_at,
            updated_at=todo.updated_at,
            recommended_skills=skill_responses,
        )
