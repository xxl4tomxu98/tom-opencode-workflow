# Agentic Todo App Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a FastAPI todo app that recommends agentic superpowers skills based on development phase.

**Architecture:** FastAPI backend with SQLAlchemy ORM, Jinja2 templates for web UI, REST API for programmatic access. Service layer handles business logic including skill injection based on todo phase.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, Jinja2, SQLite, pytest, httpx

---

## Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `app/__init__.py`
- Create: `tests/__init__.py`

**Step 1: Create requirements.txt**

```txt
fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.25
pydantic==2.5.3
jinja2==3.1.3
python-multipart==0.0.6
pytest==7.4.4
httpx==0.26.0
```

**Step 2: Create directory structure**

Run:
```bash
mkdir -p app/routers app/services app/templates/todos app/static tests
touch app/__init__.py app/routers/__init__.py app/services/__init__.py tests/__init__.py
```

**Step 3: Install dependencies**

Run: `pip install -r requirements.txt`
Expected: All packages installed successfully

**Step 4: Commit**

```bash
git add -A
git commit -m "chore: initial project setup with dependencies"
```

---

## Task 2: Database and Models

**Files:**
- Create: `app/database.py`
- Create: `app/models.py`
- Test: `tests/test_models.py`

**Step 1: Write the failing test**

Create `tests/test_models.py`:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Todo, Phase, Priority


def test_todo_model_creates_with_required_fields():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    todo = Todo(title="Test todo", phase=Phase.PLANNING, priority=Priority.MEDIUM)
    session.add(todo)
    session.commit()

    assert todo.id is not None
    assert todo.title == "Test todo"
    assert todo.phase == Phase.PLANNING
    assert todo.priority == Priority.MEDIUM
    assert todo.completed is False
    assert todo.created_at is not None
    assert todo.updated_at is not None


def test_todo_model_optional_fields():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    todo = Todo(
        title="Full todo",
        description="A description",
        phase=Phase.IMPLEMENTATION,
        priority=Priority.HIGH,
    )
    session.add(todo)
    session.commit()

    assert todo.description == "A description"
    assert todo.due_date is None


def test_phase_enum_values():
    assert Phase.PLANNING.value == "planning"
    assert Phase.DESIGN.value == "design"
    assert Phase.IMPLEMENTATION.value == "implementation"
    assert Phase.TESTING.value == "testing"
    assert Phase.DEPLOYMENT.value == "deployment"


def test_priority_enum_values():
    assert Priority.LOW.value == "low"
    assert Priority.MEDIUM.value == "medium"
    assert Priority.HIGH.value == "high"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_models.py -v`
Expected: FAIL with import errors (modules don't exist)

**Step 3: Write database.py**

Create `app/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./agentic_todo.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 4: Write models.py**

Create `app/models.py`:

```python
import enum
from datetime import datetime, date
from typing import Optional

from sqlalchemy import String, Text, Boolean, Date, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Phase(str, enum.Enum):
    PLANNING = "planning"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"


class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phase: Mapped[Phase] = mapped_column(Enum(Phase))
    priority: Mapped[Priority] = mapped_column(Enum(Priority))
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_models.py -v`
Expected: All 4 tests PASS

**Step 6: Commit**

```bash
git add -A
git commit -m "feat: add database setup and Todo model with Phase/Priority enums"
```

---

## Task 3: Config with Phase-Skills Mapping

**Files:**
- Create: `app/config.py`
- Test: `tests/test_config.py`

**Step 1: Write the failing test**

Create `tests/test_config.py`:

```python
from app.config import PHASE_SKILLS, SKILL_DETAILS, get_skills_for_phase


def test_phase_skills_mapping_has_all_phases():
    phases = ["planning", "design", "implementation", "testing", "deployment"]
    for phase in phases:
        assert phase in PHASE_SKILLS


def test_planning_phase_skills():
    skills = PHASE_SKILLS["planning"]
    assert "brainstorming" in skills
    assert "writing-plans" in skills


def test_implementation_phase_skills():
    skills = PHASE_SKILLS["implementation"]
    assert "test-driven-development" in skills
    assert "executing-plans" in skills


def test_skill_details_has_required_fields():
    for skill_name, details in SKILL_DETAILS.items():
        assert "name" in details
        assert "description" in details
        assert "when_to_use" in details


def test_get_skills_for_phase_returns_full_details():
    skills = get_skills_for_phase("planning")
    assert len(skills) >= 2
    assert skills[0]["name"] == "brainstorming"
    assert "description" in skills[0]
    assert "when_to_use" in skills[0]


def test_get_skills_for_invalid_phase_returns_empty():
    skills = get_skills_for_phase("invalid")
    assert skills == []
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with import errors

**Step 3: Write config.py**

Create `app/config.py`:

```python
from typing import List, Dict, Any

PHASE_SKILLS: Dict[str, List[str]] = {
    "planning": ["brainstorming", "writing-plans"],
    "design": ["brainstorming", "writing-plans"],
    "implementation": [
        "test-driven-development",
        "executing-plans",
        "dispatching-parallel-agents",
        "using-git-worktrees",
        "subagent-driven-development",
    ],
    "testing": [
        "test-driven-development",
        "systematic-debugging",
        "verification-before-completion",
    ],
    "deployment": [
        "finishing-a-development-branch",
        "requesting-code-review",
        "receiving-code-review",
    ],
}

SKILL_DETAILS: Dict[str, Dict[str, Any]] = {
    "brainstorming": {
        "name": "brainstorming",
        "description": "Turn ideas into fully formed designs through collaborative dialogue",
        "when_to_use": "Before any creative work - creating features, building components, "
                       "adding functionality, or modifying behavior",
        "key_steps": [
            "Check project context",
            "Ask questions one at a time",
            "Propose 2-3 approaches",
            "Present design in sections",
        ],
    },
    "writing-plans": {
        "name": "writing-plans",
        "description": "Write comprehensive implementation plans with bite-sized tasks",
        "when_to_use": "When you have a spec or requirements for a multi-step task",
        "key_steps": [
            "Break into atomic tasks",
            "Include exact file paths",
            "Write complete code snippets",
            "Add test commands",
        ],
    },
    "test-driven-development": {
        "name": "test-driven-development",
        "description": "Write tests before implementation code",
        "when_to_use": "When implementing any feature or bugfix",
        "key_steps": [
            "Write failing test first",
            "Implement minimal code to pass",
            "Refactor",
            "Repeat",
        ],
    },
    "executing-plans": {
        "name": "executing-plans",
        "description": "Execute implementation plans in separate session with review checkpoints",
        "when_to_use": "When you have a written implementation plan to execute",
        "key_steps": [
            "Review plan",
            "Set up worktree",
            "Execute task by task",
            "Verify at checkpoints",
        ],
    },
    "dispatching-parallel-agents": {
        "name": "dispatching-parallel-agents",
        "description": "Run multiple independent tasks in parallel",
        "when_to_use": "When facing 2+ independent tasks without shared state",
        "key_steps": [
            "Identify independent tasks",
            "Dispatch agents in parallel",
            "Collect results",
            "Synthesize",
        ],
    },
    "using-git-worktrees": {
        "name": "using-git-worktrees",
        "description": "Create isolated git worktrees for feature work",
        "when_to_use": "When starting feature work that needs isolation",
        "key_steps": [
            "Create worktree",
            "Verify isolation",
            "Work in worktree",
            "Merge back",
        ],
    },
    "subagent-driven-development": {
        "name": "subagent-driven-development",
        "description": "Dispatch fresh subagent per task with review between tasks",
        "when_to_use": "When executing implementation plans in current session",
        "key_steps": [
            "Load plan",
            "Dispatch subagent per task",
            "Review output",
            "Continue or fix",
        ],
    },
    "systematic-debugging": {
        "name": "systematic-debugging",
        "description": "Debug systematically before proposing fixes",
        "when_to_use": "When encountering any bug, test failure, or unexpected behavior",
        "key_steps": [
            "Reproduce the issue",
            "Form hypothesis",
            "Test hypothesis",
            "Fix root cause",
        ],
    },
    "verification-before-completion": {
        "name": "verification-before-completion",
        "description": "Run verification commands before claiming work is complete",
        "when_to_use": "Before committing or creating PRs",
        "key_steps": [
            "Run tests",
            "Check linting",
            "Verify build",
            "Confirm output",
        ],
    },
    "finishing-a-development-branch": {
        "name": "finishing-a-development-branch",
        "description": "Guide completion of development work with structured options",
        "when_to_use": "When implementation is complete and all tests pass",
        "key_steps": [
            "Verify all tests pass",
            "Choose merge strategy",
            "Create PR or merge",
            "Clean up",
        ],
    },
    "requesting-code-review": {
        "name": "requesting-code-review",
        "description": "Request code review to verify work meets requirements",
        "when_to_use": "When completing tasks or before merging",
        "key_steps": [
            "Summarize changes",
            "Highlight concerns",
            "Request specific feedback",
            "Address feedback",
        ],
    },
    "receiving-code-review": {
        "name": "receiving-code-review",
        "description": "Handle code review feedback with technical rigor",
        "when_to_use": "When receiving feedback, especially if unclear or questionable",
        "key_steps": [
            "Understand feedback",
            "Verify claims",
            "Implement valid suggestions",
            "Push back if needed",
        ],
    },
}


def get_skills_for_phase(phase: str) -> List[Dict[str, Any]]:
    """Get full skill details for a given phase."""
    skill_names = PHASE_SKILLS.get(phase, [])
    return [SKILL_DETAILS[name] for name in skill_names if name in SKILL_DETAILS]
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: All 6 tests PASS

**Step 5: Commit**

```bash
git add -A
git commit -m "feat: add phase-skills mapping and skill details config"
```

---

## Task 4: Pydantic Schemas

**Files:**
- Create: `app/schemas.py`
- Test: `tests/test_schemas.py`

**Step 1: Write the failing test**

Create `tests/test_schemas.py`:

```python
import pytest
from datetime import date
from pydantic import ValidationError

from app.schemas import (
    TodoCreate,
    TodoUpdate,
    TodoResponse,
    SkillResponse,
    PhaseResponse,
)
from app.models import Phase, Priority


def test_todo_create_minimal():
    todo = TodoCreate(title="Test", phase=Phase.PLANNING, priority=Priority.LOW)
    assert todo.title == "Test"
    assert todo.phase == Phase.PLANNING
    assert todo.description is None


def test_todo_create_full():
    todo = TodoCreate(
        title="Full todo",
        description="Description",
        phase=Phase.DESIGN,
        priority=Priority.HIGH,
        due_date=date(2026, 2, 15),
    )
    assert todo.due_date == date(2026, 2, 15)


def test_todo_create_title_too_long():
    with pytest.raises(ValidationError):
        TodoCreate(
            title="x" * 201,
            phase=Phase.PLANNING,
            priority=Priority.LOW,
        )


def test_todo_update_partial():
    update = TodoUpdate(title="New title")
    assert update.title == "New title"
    assert update.phase is None
    assert update.completed is None


def test_skill_response():
    skill = SkillResponse(
        name="test-skill",
        description="A test skill",
        when_to_use="When testing",
    )
    assert skill.name == "test-skill"


def test_phase_response():
    phase = PhaseResponse(
        name="planning",
        skills=[
            SkillResponse(
                name="brainstorming",
                description="Turn ideas into designs",
                when_to_use="Before creative work",
            )
        ],
    )
    assert phase.name == "planning"
    assert len(phase.skills) == 1
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_schemas.py -v`
Expected: FAIL with import errors

**Step 3: Write schemas.py**

Create `app/schemas.py`:

```python
from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.models import Phase, Priority


class SkillResponse(BaseModel):
    name: str
    description: str
    when_to_use: str
    key_steps: Optional[List[str]] = None


class TodoBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    phase: Phase
    priority: Priority
    due_date: Optional[date] = None


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    phase: Optional[Phase] = None
    priority: Optional[Priority] = None
    due_date: Optional[date] = None
    completed: Optional[bool] = None


class TodoResponse(TodoBase):
    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime
    recommended_skills: List[SkillResponse] = []

    class Config:
        from_attributes = True


class PhaseResponse(BaseModel):
    name: str
    skills: List[SkillResponse]
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_schemas.py -v`
Expected: All 6 tests PASS

**Step 5: Commit**

```bash
git add -A
git commit -m "feat: add Pydantic schemas for todos and skills"
```

---

## Task 5: Todo Service Layer

**Files:**
- Create: `app/services/todo_service.py`
- Test: `tests/test_service.py`

**Step 1: Write the failing test**

Create `tests/test_service.py`:

```python
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Todo, Phase, Priority
from app.services.todo_service import TodoService
from app.schemas import TodoCreate, TodoUpdate


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def todo_service(db_session):
    return TodoService(db_session)


def test_create_todo(todo_service):
    data = TodoCreate(title="New todo", phase=Phase.PLANNING, priority=Priority.MEDIUM)
    todo = todo_service.create(data)

    assert todo.id is not None
    assert todo.title == "New todo"
    assert todo.phase == Phase.PLANNING


def test_get_todo(todo_service, db_session):
    data = TodoCreate(title="Get me", phase=Phase.DESIGN, priority=Priority.LOW)
    created = todo_service.create(data)

    fetched = todo_service.get(created.id)
    assert fetched is not None
    assert fetched.title == "Get me"


def test_get_todo_not_found(todo_service):
    result = todo_service.get(999)
    assert result is None


def test_list_todos(todo_service):
    todo_service.create(TodoCreate(title="One", phase=Phase.PLANNING, priority=Priority.LOW))
    todo_service.create(TodoCreate(title="Two", phase=Phase.DESIGN, priority=Priority.HIGH))

    todos = todo_service.list()
    assert len(todos) == 2


def test_list_todos_filter_by_phase(todo_service):
    todo_service.create(TodoCreate(title="Planning", phase=Phase.PLANNING, priority=Priority.LOW))
    todo_service.create(TodoCreate(title="Design", phase=Phase.DESIGN, priority=Priority.LOW))

    todos = todo_service.list(phase=Phase.PLANNING)
    assert len(todos) == 1
    assert todos[0].title == "Planning"


def test_list_todos_filter_by_completed(todo_service):
    todo = todo_service.create(
        TodoCreate(title="Done", phase=Phase.TESTING, priority=Priority.LOW)
    )
    todo_service.toggle_complete(todo.id)
    todo_service.create(
        TodoCreate(title="Not done", phase=Phase.TESTING, priority=Priority.LOW)
    )

    completed = todo_service.list(completed=True)
    assert len(completed) == 1
    assert completed[0].title == "Done"


def test_update_todo(todo_service):
    todo = todo_service.create(
        TodoCreate(title="Original", phase=Phase.PLANNING, priority=Priority.LOW)
    )
    updated = todo_service.update(todo.id, TodoUpdate(title="Updated", priority=Priority.HIGH))

    assert updated.title == "Updated"
    assert updated.priority == Priority.HIGH
    assert updated.phase == Phase.PLANNING  # unchanged


def test_delete_todo(todo_service):
    todo = todo_service.create(
        TodoCreate(title="Delete me", phase=Phase.PLANNING, priority=Priority.LOW)
    )
    result = todo_service.delete(todo.id)
    assert result is True

    fetched = todo_service.get(todo.id)
    assert fetched is None


def test_toggle_complete(todo_service):
    todo = todo_service.create(
        TodoCreate(title="Toggle", phase=Phase.PLANNING, priority=Priority.LOW)
    )
    assert todo.completed is False

    toggled = todo_service.toggle_complete(todo.id)
    assert toggled.completed is True

    toggled_again = todo_service.toggle_complete(todo.id)
    assert toggled_again.completed is False


def test_get_with_skills(todo_service):
    todo = todo_service.create(
        TodoCreate(title="With skills", phase=Phase.PLANNING, priority=Priority.LOW)
    )
    response = todo_service.get_with_skills(todo.id)

    assert response is not None
    assert len(response.recommended_skills) >= 2
    assert response.recommended_skills[0].name == "brainstorming"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_service.py -v`
Expected: FAIL with import errors

**Step 3: Write todo_service.py**

Create `app/services/todo_service.py`:

```python
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_service.py -v`
Expected: All 11 tests PASS

**Step 5: Commit**

```bash
git add -A
git commit -m "feat: add TodoService with CRUD and skill injection"
```

---

## Task 6: Test Fixtures (conftest.py)

**Files:**
- Create: `tests/conftest.py`

**Step 1: Create conftest.py**

Create `tests/conftest.py`:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app


@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

**Step 2: Commit (will fully work after main.py is created)**

```bash
git add tests/conftest.py
git commit -m "feat: add test fixtures with in-memory DB and test client"
```

---

## Task 7: API Router

**Files:**
- Create: `app/routers/api.py`
- Test: `tests/test_api.py`

**Step 1: Write the failing test**

Create `tests/test_api.py`:

```python
import pytest
from fastapi.testclient import TestClient


def test_create_todo(client):
    response = client.post(
        "/api/todos",
        json={
            "title": "Test todo",
            "phase": "planning",
            "priority": "medium",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test todo"
    assert data["phase"] == "planning"
    assert "id" in data
    assert "recommended_skills" in data


def test_list_todos(client):
    client.post(
        "/api/todos",
        json={"title": "One", "phase": "planning", "priority": "low"},
    )
    client.post(
        "/api/todos",
        json={"title": "Two", "phase": "design", "priority": "high"},
    )

    response = client.get("/api/todos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_todos_filter_by_phase(client):
    client.post(
        "/api/todos",
        json={"title": "Planning", "phase": "planning", "priority": "low"},
    )
    client.post(
        "/api/todos",
        json={"title": "Design", "phase": "design", "priority": "low"},
    )

    response = client.get("/api/todos?phase=planning")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Planning"


def test_get_todo(client):
    create_response = client.post(
        "/api/todos",
        json={"title": "Get me", "phase": "implementation", "priority": "high"},
    )
    todo_id = create_response.json()["id"]

    response = client.get(f"/api/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Get me"
    assert len(data["recommended_skills"]) >= 1


def test_get_todo_not_found(client):
    response = client.get("/api/todos/999")
    assert response.status_code == 404


def test_update_todo(client):
    create_response = client.post(
        "/api/todos",
        json={"title": "Original", "phase": "planning", "priority": "low"},
    )
    todo_id = create_response.json()["id"]

    response = client.put(
        f"/api/todos/{todo_id}",
        json={"title": "Updated", "priority": "high"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["priority"] == "high"


def test_delete_todo(client):
    create_response = client.post(
        "/api/todos",
        json={"title": "Delete me", "phase": "testing", "priority": "low"},
    )
    todo_id = create_response.json()["id"]

    response = client.delete(f"/api/todos/{todo_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/todos/{todo_id}")
    assert get_response.status_code == 404


def test_toggle_complete(client):
    create_response = client.post(
        "/api/todos",
        json={"title": "Toggle", "phase": "deployment", "priority": "medium"},
    )
    todo_id = create_response.json()["id"]
    assert create_response.json()["completed"] is False

    response = client.patch(f"/api/todos/{todo_id}/complete")
    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_list_phases(client):
    response = client.get("/api/phases")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    phase_names = [p["name"] for p in data]
    assert "planning" in phase_names
    assert "deployment" in phase_names


def test_get_phase(client):
    response = client.get("/api/phases/implementation")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "implementation"
    assert len(data["skills"]) >= 1


def test_get_phase_not_found(client):
    response = client.get("/api/phases/invalid")
    assert response.status_code == 404
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_api.py -v`
Expected: FAIL with import errors (main.py doesn't exist)

**Step 3: Write api.py**

Create `app/routers/api.py`:

```python
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
```

**Step 4: Create main.py (minimal for API tests)**

Create `app/main.py`:

```python
from fastapi import FastAPI

from app.database import engine, Base
from app.routers import api

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agentic Todo", description="Todo app with agentic skill recommendations")

app.include_router(api.router)
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_api.py -v`
Expected: All 12 tests PASS

**Step 6: Commit**

```bash
git add -A
git commit -m "feat: add REST API endpoints for todos and phases"
```

---

## Task 8: Web Router (HTML Templates)

**Files:**
- Create: `app/routers/web.py`
- Create: `app/templates/base.html`
- Create: `app/templates/index.html`
- Create: `app/templates/todos/list.html`
- Create: `app/templates/todos/detail.html`
- Create: `app/templates/todos/form.html`
- Create: `app/templates/phases.html`
- Create: `app/static/style.css`
- Modify: `app/main.py`

**Step 1: Create base.html**

Create `app/templates/base.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Agentic Todo{% endblock %}</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <nav>
        <div class="nav-brand"><a href="/">Agentic Todo</a></div>
        <div class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/todos">Todos</a>
            <a href="/phases">Phases</a>
            <a href="/todos/new" class="btn-new">+ New Todo</a>
        </div>
    </nav>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

**Step 2: Create index.html (Dashboard)**

Create `app/templates/index.html`:

```html
{% extends "base.html" %}

{% block title %}Dashboard - Agentic Todo{% endblock %}

{% block content %}
<h1>Dashboard</h1>

<div class="phase-tabs">
    {% for phase_name in phases %}
    <span class="phase-tab">{{ phase_name|capitalize }} ({{ todos_by_phase[phase_name]|length }})</span>
    {% endfor %}
</div>

{% for phase_name, phase_todos in todos_by_phase.items() %}
{% if phase_todos %}
<section class="phase-section">
    <h2>{{ phase_name|capitalize }}</h2>
    <ul class="todo-list">
        {% for todo in phase_todos %}
        <li class="todo-item {% if todo.completed %}completed{% endif %}">
            <a href="/todos/{{ todo.id }}">
                <span class="todo-checkbox">{% if todo.completed %}☑{% else %}☐{% endif %}</span>
                <span class="todo-title">{{ todo.title }}</span>
                <span class="todo-priority priority-{{ todo.priority.value }}">{{ todo.priority.value|upper }}</span>
                {% if todo.due_date %}
                <span class="todo-due">Due: {{ todo.due_date }}</span>
                {% endif %}
            </a>
        </li>
        {% endfor %}
    </ul>
    <div class="phase-skills">
        💡 Recommended: {{ skills_by_phase[phase_name]|join(", ") }}
    </div>
</section>
{% endif %}
{% endfor %}

{% if not todos_by_phase.values()|sum(start=[]) %}
<p class="empty-state">No todos yet. <a href="/todos/new">Create one</a>.</p>
{% endif %}
{% endblock %}
```

**Step 3: Create todos/list.html**

Create `app/templates/todos/list.html`:

```html
{% extends "base.html" %}

{% block title %}Todos - Agentic Todo{% endblock %}

{% block content %}
<h1>All Todos</h1>

<form class="filters" method="get">
    <select name="phase">
        <option value="">All Phases</option>
        {% for p in phases %}
        <option value="{{ p }}" {% if phase == p %}selected{% endif %}>{{ p|capitalize }}</option>
        {% endfor %}
    </select>
    <select name="priority">
        <option value="">All Priorities</option>
        {% for p in priorities %}
        <option value="{{ p }}" {% if priority == p %}selected{% endif %}>{{ p|capitalize }}</option>
        {% endfor %}
    </select>
    <select name="completed">
        <option value="">All Status</option>
        <option value="true" {% if completed == "true" %}selected{% endif %}>Completed</option>
        <option value="false" {% if completed == "false" %}selected{% endif %}>Pending</option>
    </select>
    <button type="submit">Filter</button>
</form>

<ul class="todo-list">
    {% for todo in todos %}
    <li class="todo-item {% if todo.completed %}completed{% endif %}">
        <a href="/todos/{{ todo.id }}">
            <span class="todo-checkbox">{% if todo.completed %}☑{% else %}☐{% endif %}</span>
            <span class="todo-title">{{ todo.title }}</span>
            <span class="todo-phase">{{ todo.phase.value|capitalize }}</span>
            <span class="todo-priority priority-{{ todo.priority.value }}">{{ todo.priority.value|upper }}</span>
        </a>
    </li>
    {% else %}
    <li class="empty-state">No todos match your filters.</li>
    {% endfor %}
</ul>
{% endblock %}
```

**Step 4: Create todos/detail.html**

Create `app/templates/todos/detail.html`:

```html
{% extends "base.html" %}

{% block title %}{{ todo.title }} - Agentic Todo{% endblock %}

{% block content %}
<div class="todo-detail">
    <div class="todo-header">
        <h1>{{ todo.title }}</h1>
        <div class="todo-actions">
            <a href="/todos/{{ todo.id }}/edit" class="btn">Edit</a>
            <form method="post" action="/todos/{{ todo.id }}/toggle" style="display:inline">
                <button type="submit" class="btn">
                    {% if todo.completed %}Mark Incomplete{% else %}Mark Complete{% endif %}
                </button>
            </form>
            <form method="post" action="/todos/{{ todo.id }}/delete" style="display:inline">
                <button type="submit" class="btn btn-danger">Delete</button>
            </form>
        </div>
    </div>

    <div class="todo-meta">
        <span class="todo-phase">Phase: {{ todo.phase.value|capitalize }}</span>
        <span class="todo-priority priority-{{ todo.priority.value }}">{{ todo.priority.value|upper }}</span>
        {% if todo.due_date %}
        <span class="todo-due">Due: {{ todo.due_date }}</span>
        {% endif %}
        <span class="todo-status">{% if todo.completed %}✓ Completed{% else %}○ Pending{% endif %}</span>
    </div>

    {% if todo.description %}
    <div class="todo-description">
        <h3>Description</h3>
        <p>{{ todo.description }}</p>
    </div>
    {% endif %}

    <div class="recommended-skills">
        <h2>Recommended for {{ todo.phase.value|capitalize }} Phase</h2>
        {% for skill in recommended_skills %}
        <div class="skill-card">
            <h3>📘 {{ skill.name }}</h3>
            <p>{{ skill.description }}</p>
            <p><strong>Use when:</strong> {{ skill.when_to_use }}</p>
            {% if skill.key_steps %}
            <p><strong>Steps:</strong> {{ skill.key_steps|join(" → ") }}</p>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
```

**Step 5: Create todos/form.html**

Create `app/templates/todos/form.html`:

```html
{% extends "base.html" %}

{% block title %}{% if todo %}Edit{% else %}New{% endif %} Todo - Agentic Todo{% endblock %}

{% block content %}
<h1>{% if todo %}Edit Todo{% else %}New Todo{% endif %}</h1>

<form method="post" class="todo-form">
    <div class="form-group">
        <label for="title">Title</label>
        <input type="text" id="title" name="title" required maxlength="200"
               value="{{ todo.title if todo else '' }}">
    </div>

    <div class="form-group">
        <label for="description">Description</label>
        <textarea id="description" name="description" rows="4">{{ todo.description if todo and todo.description else '' }}</textarea>
    </div>

    <div class="form-row">
        <div class="form-group">
            <label for="phase">Phase</label>
            <select id="phase" name="phase" required>
                {% for p in phases %}
                <option value="{{ p }}" {% if todo and todo.phase.value == p %}selected{% endif %}>
                    {{ p|capitalize }}
                </option>
                {% endfor %}
            </select>
        </div>

        <div class="form-group">
            <label for="priority">Priority</label>
            <select id="priority" name="priority" required>
                {% for p in priorities %}
                <option value="{{ p }}" {% if todo and todo.priority.value == p %}selected{% endif %}>
                    {{ p|capitalize }}
                </option>
                {% endfor %}
            </select>
        </div>

        <div class="form-group">
            <label for="due_date">Due Date</label>
            <input type="date" id="due_date" name="due_date"
                   value="{{ todo.due_date if todo and todo.due_date else '' }}">
        </div>
    </div>

    <div class="form-actions">
        <button type="submit" class="btn btn-primary">
            {% if todo %}Update{% else %}Create{% endif %} Todo
        </button>
        <a href="{% if todo %}/todos/{{ todo.id }}{% else %}/{% endif %}" class="btn">Cancel</a>
    </div>
</form>
{% endblock %}
```

**Step 6: Create phases.html**

Create `app/templates/phases.html`:

```html
{% extends "base.html" %}

{% block title %}Phases - Agentic Todo{% endblock %}

{% block content %}
<h1>Development Phases & Recommended Skills</h1>

{% for phase in phases %}
<section class="phase-detail">
    <h2>{{ phase.name|capitalize }}</h2>
    <div class="skills-grid">
        {% for skill in phase.skills %}
        <div class="skill-card">
            <h3>📘 {{ skill.name }}</h3>
            <p>{{ skill.description }}</p>
            <p><strong>Use when:</strong> {{ skill.when_to_use }}</p>
            {% if skill.key_steps %}
            <div class="skill-steps">
                <strong>Steps:</strong>
                <ol>
                    {% for step in skill.key_steps %}
                    <li>{{ step }}</li>
                    {% endfor %}
                </ol>
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</section>
{% endfor %}
{% endblock %}
```

**Step 7: Create style.css**

Create `app/static/style.css`:

```css
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    background: #f5f5f5;
}

nav {
    background: #2c3e50;
    color: white;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-brand a {
    color: white;
    text-decoration: none;
    font-size: 1.25rem;
    font-weight: bold;
}

.nav-links a {
    color: #ecf0f1;
    text-decoration: none;
    margin-left: 1.5rem;
}

.nav-links a:hover {
    color: white;
}

.btn-new {
    background: #27ae60;
    padding: 0.5rem 1rem;
    border-radius: 4px;
}

main {
    max-width: 1000px;
    margin: 2rem auto;
    padding: 0 1rem;
}

h1 {
    margin-bottom: 1.5rem;
    color: #2c3e50;
}

h2 {
    margin: 1.5rem 0 1rem;
    color: #34495e;
}

.phase-tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}

.phase-tab {
    background: #ecf0f1;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-size: 0.9rem;
}

.phase-section {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.todo-list {
    list-style: none;
}

.todo-item {
    border-bottom: 1px solid #ecf0f1;
}

.todo-item:last-child {
    border-bottom: none;
}

.todo-item a {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 0;
    text-decoration: none;
    color: inherit;
}

.todo-item.completed .todo-title {
    text-decoration: line-through;
    color: #95a5a6;
}

.todo-checkbox {
    font-size: 1.25rem;
}

.todo-title {
    flex: 1;
}

.todo-priority {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-weight: bold;
}

.priority-low {
    background: #d5f5e3;
    color: #27ae60;
}

.priority-medium {
    background: #fef9e7;
    color: #f39c12;
}

.priority-high {
    background: #fadbd8;
    color: #e74c3c;
}

.todo-due {
    font-size: 0.85rem;
    color: #7f8c8d;
}

.todo-phase {
    font-size: 0.85rem;
    color: #7f8c8d;
    background: #ecf0f1;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
}

.phase-skills {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #ecf0f1;
    font-size: 0.9rem;
    color: #7f8c8d;
}

.empty-state {
    text-align: center;
    padding: 3rem;
    color: #7f8c8d;
}

.filters {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}

.filters select,
.filters button {
    padding: 0.5rem 1rem;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    font-size: 1rem;
}

.filters button {
    background: #3498db;
    color: white;
    border: none;
    cursor: pointer;
}

.todo-detail {
    background: white;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.todo-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.todo-actions {
    display: flex;
    gap: 0.5rem;
}

.btn {
    padding: 0.5rem 1rem;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    background: white;
    cursor: pointer;
    text-decoration: none;
    color: #333;
    font-size: 0.9rem;
}

.btn-primary {
    background: #3498db;
    color: white;
    border-color: #3498db;
}

.btn-danger {
    background: #e74c3c;
    color: white;
    border-color: #e74c3c;
}

.todo-meta {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}

.todo-description {
    margin-bottom: 2rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 4px;
}

.recommended-skills {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 2px solid #ecf0f1;
}

.skill-card {
    background: #f8f9fa;
    border-left: 4px solid #3498db;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 0 4px 4px 0;
}

.skill-card h3 {
    margin-bottom: 0.5rem;
    color: #2c3e50;
}

.skill-card p {
    margin-bottom: 0.5rem;
}

.skills-grid {
    display: grid;
    gap: 1rem;
}

.todo-form {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.form-group input,
.form-group textarea,
.form-group select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    font-size: 1rem;
}

.form-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
}

.form-actions {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
}

.phase-detail {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.skill-steps ol {
    margin-left: 1.5rem;
    margin-top: 0.5rem;
}
```

**Step 8: Create web.py router**

Create `app/routers/web.py`:

```python
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
        return RedirectResponse(url="/", status_code=303)

    skills = get_skills_for_phase(todo.phase.value)
    skill_responses = [SkillResponse(**skill) for skill in skills]

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
        return RedirectResponse(url="/", status_code=303)

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
def phases_page(request: Request):
    phases_data = []
    for phase_name in PHASES:
        skills = get_skills_for_phase(phase_name)
        phases_data.append(
            {
                "name": phase_name,
                "skills": [SkillResponse(**s) for s in skills],
            }
        )

    return templates.TemplateResponse(
        "phases.html",
        {"request": request, "phases": phases_data},
    )
```

**Step 9: Update main.py to include web router and static files**

Update `app/main.py`:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
from app.routers import api, web

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agentic Todo", description="Todo app with agentic skill recommendations")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(api.router)
app.include_router(web.router)
```

**Step 10: Run all tests**

Run: `pytest -v`
Expected: All tests PASS

**Step 11: Commit**

```bash
git add -A
git commit -m "feat: add web UI with Jinja2 templates and CSS styling"
```

---

## Task 9: Manual Verification

**Step 1: Start the server**

Run: `uvicorn app.main:app --reload`
Expected: Server starts on http://127.0.0.1:8000

**Step 2: Verify endpoints**

- Open http://127.0.0.1:8000 - Dashboard should load
- Open http://127.0.0.1:8000/docs - Swagger UI should show API docs
- Create a todo via the UI
- Verify skill recommendations appear on todo detail page

**Step 3: Final commit**

```bash
git add -A
git commit -m "chore: finalize agentic todo app implementation"
```

---

## Summary

| Task | Description | Tests |
|------|-------------|-------|
| 1 | Project setup | - |
| 2 | Database & models | 4 |
| 3 | Config with skills | 6 |
| 4 | Pydantic schemas | 6 |
| 5 | Todo service | 11 |
| 6 | Test fixtures | - |
| 7 | API router | 12 |
| 8 | Web UI | - |
| 9 | Manual verification | - |

**Total: ~39 automated tests**
