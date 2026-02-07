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
