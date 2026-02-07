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
    assert updated.phase == Phase.PLANNING


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
