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
