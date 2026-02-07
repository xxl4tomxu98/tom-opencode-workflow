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
