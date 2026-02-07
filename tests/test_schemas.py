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
