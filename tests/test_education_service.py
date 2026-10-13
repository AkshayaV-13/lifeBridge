"""
Unit tests for Education Service.
Verifies Class 6 residential school admissions, Class 11 separation,
college scholarships, NEET entrance exams, income uncertainty, deadline labeling,
and safe fallback handling.
"""

import pytest
from services.education_service import EducationService


@pytest.fixture
def service():
    return EducationService()


def test_real_dataset_loads_ten_schemes(service):
    schemes = service.load_schemes()
    assert len(schemes) >= 10
    ids = [s["scheme_id"] for s in schemes]
    assert "EDU-JNVST-CL6" in ids
    assert "EDU-NMMS" in ids
    assert "EDU-NEET-UG" in ids
    assert "EDU-PM-USP-CSSS" in ids
    assert "EDU-SSP-POSTMATRIC-KA" in ids


def test_class_6_student_receives_school_admission(service):
    """
    TEST 1: A Class 6 / 5 student receives relevant school admission opportunities (JNVST)
    rather than unrelated college scholarships.
    """
    profile = {
        "current_class": "Class 5",
        "education_level": "School Education",
        "assistance_type": "Government & Residential Schools",
        "state": "Karnataka"
    }

    matches = service.get_actionable_matches(profile)
    assert len(matches) > 0
    top_scheme_id = matches[0].scheme["scheme_id"]
    assert top_scheme_id == "EDU-JNVST-CL6"
    assert "Navodaya" in matches[0].scheme["name"]

    # Verify college scholarship is not the top actionable recommendation
    college_schemes = [m for m in matches if "Undergraduate" in str(m.scheme.get("education_levels", []))]
    assert len(college_schemes) == 0


def test_class_11_student_not_given_class_6_admission(service):
    """
    TEST 2: A Class 11 student is NOT incorrectly given a Class 6 admission procedure.
    """
    profile = {
        "current_class": "Class 11",
        "education_level": "Pre-University",
        "state": "Karnataka"
    }

    all_results = service.match_schemes(profile)
    jnv_result = next((r for r in all_results if r.scheme["scheme_id"] == "EDU-JNVST-CL6"), None)

    assert jnv_result is not None
    assert jnv_result.status_label == "Not a Match — Mandatory Requirement Not Met"
    assert any("strictly for Class 5 students" in u for u in jnv_result.unmet_criteria)


def test_college_student_receives_higher_education_scholarship(service):
    """
    TEST 3: A college student receives potentially relevant higher-education scholarships.
    """
    profile = {
        "current_class": "Undergraduate (BTech)",
        "education_level": "Undergraduate",
        "course": "Engineering / BTech",
        "family_income": 200000,
        "state": "Karnataka",
        "assistance_type": "Scholarships"
    }

    matches = service.get_actionable_matches(profile)
    assert len(matches) > 0
    match_ids = [m.scheme["scheme_id"] for m in matches]
    assert any(s in match_ids for s in ["EDU-PM-USP-CSSS", "EDU-SSP-POSTMATRIC-KA", "EDU-AICTE-PRAGATI"])


def test_exam_request_produces_official_exam_info(service):
    """
    TEST 4: An examination request (NEET) produces official exam info rather than unrelated scholarships.
    """
    profile = {
        "target_exam": "NEET-UG",
        "assistance_type": "Entrance Examinations",
        "current_class": "Class 12"
    }

    matches = service.get_actionable_matches(profile)
    assert len(matches) > 0
    top = matches[0]
    assert top.scheme["scheme_id"] == "EDU-NEET-UG"
    assert top.scheme["programme_type"] == "Entrance Examination"
    assert "exams.nta.ac.in" in top.scheme["official_information_url"]


def test_missing_income_produces_uncertainty_message(service):
    """
    TEST 5: Missing income produces an appropriate uncertainty message when required.
    """
    profile = {
        "current_class": "Class 8",
        "education_level": "School Education",
        "state": "Karnataka"
        # income not provided
    }

    all_results = service.match_schemes(profile)
    nmms = next((r for r in all_results if r.scheme["scheme_id"] == "EDU-NMMS"), None)
    assert nmms is not None
    assert any("income" in m.lower() for m in nmms.missing_information)


def test_deadline_not_presented_as_unverified_current(service):
    """
    TEST 6: An expired or unverified deadline is NOT presented as current.
    """
    schemes = service.load_schemes()
    for s in schemes:
        dl = s.get("application_deadline", "")
        # Should contain verification caution rather than claiming an old static deadline
        assert "needs verification" in dl.lower() or "check" in dl.lower()


def test_no_match_produces_helpful_fallback(service):
    """
    TEST 7: No matching opportunity produces helpful fallback.
    """
    profile = {
        "current_class": "Class 1",
        "state": "NonExistentState123",
        "family_income": 99999999,
        "assistance_type": "Entrance Examinations",
        "target_exam": "UnknownExam99"
    }

    matches = service.get_actionable_matches(profile)
    assert len(matches) == 0
    # Service still returns evaluated results without crashing
    all_res = service.match_schemes(profile)
    assert len(all_res) > 0
