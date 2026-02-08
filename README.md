# tom-opencode-workflow
# Agentic Todo App Design

## Overview

A self-referential todo app that recommends agentic methods at each development stage. The app practices what it preaches—using your oh-my-opencode and superpowers skills to guide development workflows.

## Core Concept

- Each todo has a **phase**: Planning → Design → Implementation → Testing → Deployment
- Each phase maps to relevant **superpowers skills**
- When viewing a todo, the app shows recommended agentic approaches for that phase

## Data Model

### Todo

| Field | Type | Notes |
|-------|------|-------|
| id | int | Primary key |
| title | str | Required, max 200 chars |
| description | str | Optional, text |
| phase | enum | planning, design, implementation, testing, deployment |
| priority | enum | low, medium, high |
| due_date | date | Optional |
| completed | bool | Default false |
| created_at | datetime | Auto |
| updated_at | datetime | Auto |

### Phase-to-Skills Mapping

```python
PHASE_SKILLS = {
    "planning": ["brainstorming", "writing-plans"],
    "design": ["brainstorming", "writing-plans"],
    "implementation": [
        "test-driven-development",
        "executing-plans",
        "dispatching-parallel-agents",
        "using-git-worktrees",
        "subagent-driven-development"
    ],
    "testing": [
        "test-driven-development",
        "systematic-debugging",
        "verification-before-completion"
    ],
    "deployment": [
        "finishing-a-development-branch",
        "requesting-code-review",
        "receiving-code-review"
    ],
}
```

## API Structure

### REST Endpoints

```
Todos CRUD:
GET    /api/todos          - List all (filter: phase, completed, priority)
POST   /api/todos          - Create todo
GET    /api/todos/{id}     - Get single todo + recommended skills
PUT    /api/todos/{id}     - Update todo
DELETE /api/todos/{id}     - Delete todo
PATCH  /api/todos/{id}/complete - Toggle completion

Skills Reference:
GET    /api/phases         - List all phases with mapped skills
GET    /api/phases/{phase} - Get phase with full skill details
```

### Response Shape

```json
{
  "id": 1,
  "title": "Design user auth flow",
  "description": "OAuth2 with Google",
  "phase": "design",
  "priority": "high",
  "due_date": "2026-02-10",
  "completed": false,
  "created_at": "2026-02-06T20:00:00Z",
  "updated_at": "2026-02-06T20:00:00Z",
  "recommended_skills": [
    {"name": "brainstorming", "description": "...", "when_to_use": "..."}
  ]
}
```

## Web UI

### Routes

```
GET /                    - Dashboard (todos grouped by phase)
GET /todos               - Todo list with filters
GET /todos/new           - Create form
GET /todos/{id}          - Detail + recommended skills panel
GET /todos/{id}/edit     - Edit form
GET /phases              - Skill reference page
```

### Dashboard Layout

```
┌─────────────────────────────────────────────────────────────-┐
│  Agentic Todo                                    [+ New Todo]│
├────────────────────────────────────────────────────────────-─┤
│  Planning (2)  │  Design (1)  │  Impl (3)  │  Test  │  Deploy│
├────────────────────────────────────────────────────────────-─┤
│  ┌─ Planning ──────────────────────────────────────────┐     │
│  │ ☐ Define project scope           HIGH   Due: Feb 10 │     │
│  │ ☐ Gather requirements            MED                │     │
│  │ 💡 Recommended: brainstorming, writing-plans        │     │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
tom-opencode-workflow/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, startup
│   ├── config.py            # Settings, PHASE_SKILLS mapping
│   ├── database.py          # SQLAlchemy engine, session
│   ├── models.py            # Todo model
│   ├── schemas.py           # Pydantic schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── api.py           # REST endpoints
│   │   └── web.py           # HTML routes
│   ├── services/
│   │   ├── __init__.py
│   │   └── todo_service.py  # Business logic
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── todos/
│   │   │   ├── list.html
│   │   │   ├── detail.html
│   │   │   └── form.html
│   │   └── phases.html
│   └── static/
│       └── style.css
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   └── test_service.py
├── requirements.txt
└── README.md
```

## Dependencies

- fastapi
- uvicorn
- sqlalchemy
- pydantic
- jinja2
- python-multipart
- pytest
- httpx

## Implementation Approach

Use TDD (test-driven development):
1. Write failing test
2. Implement minimal code to pass
3. Refactor
4. Repeat

## Skill Content

Each skill shows:
- **name**: Skill identifier
- **description**: What it does
- **when_to_use**: Trigger conditions
- **key_steps**: High-level workflow

Content is read from actual superpowers skill files.

