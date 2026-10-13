"""
Integration tests for LifeBridge platform across Healthcare, Education, and Food modules.
Verifies all 3 modules are importable, function cleanly, and maintain session state.
"""

import pytest
from services.scheme_matcher import SchemeMatcher
from services.hospital_service import HospitalService
from services.conversation_service import ConversationService
from services.education_service import EducationService
from services.food_services_service import FoodServicesService


def test_healthcare_module_intact_and_functional():
    """
    INTEGRATION TEST 1: Existing Healthcare module still loads and evaluates schemes.
    """
    matcher = SchemeMatcher()
    schemes = matcher.load_schemes()
    assert len(schemes) >= 10

    hosp_service = HospitalService()
    hospitals = hosp_service.load_hospitals()
    assert len(hospitals) >= 10

    conv_service = ConversationService()
    extracted = conv_service.extract_entities(
        "I have cancer and need chemotherapy in Bengaluru", {}
    )
    assert extracted.get("condition") == "cancer"
    assert extracted.get("city") == "Bengaluru"


def test_education_module_functional():
    """
    INTEGRATION TEST 2: Education module loads and evaluates accurately.
    """
    edu_service = EducationService()
    schemes = edu_service.load_schemes()
    assert len(schemes) >= 10

    profile = {"current_class": "Class 12", "target_exam": "NEET-UG"}
    matches = edu_service.get_actionable_matches(profile)
    assert len(matches) > 0
    assert matches[0].scheme["scheme_id"] == "EDU-NEET-UG"


def test_food_services_module_functional():
    """
    INTEGRATION TEST 3: Food & Essential Services module loads and matches.
    """
    food_service = FoodServicesService()
    services = food_service.load_services()
    assert len(services) >= 10

    centres = food_service.load_centres()
    assert len(centres) >= 10

    profile = {"service_category": "Check Portability (One Nation One Ration Card)"}
    matches = food_service.get_actionable_matches(profile)
    assert len(matches) > 0
    assert matches[0].service["service_id"] == "FOOD-ONORC"


def test_all_modules_run_offline_without_api_keys():
    """
    INTEGRATION TEST 4: Verifies all modules run without any external LLM API key.
    """
    import os
    # Temporarily ensure no API keys are required
    old_gemini = os.environ.get("GEMINI_API_KEY")
    old_openai = os.environ.get("OPENAI_API_KEY")
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]

    try:
        matcher = SchemeMatcher()
        h_res = matcher.match_schemes({"state": "Karnataka", "condition": "cardiac"})
        assert len(h_res) > 0

        edu = EducationService()
        e_res = edu.match_schemes({"current_class": "Class 5"})
        assert len(e_res) > 0

        food = FoodServicesService()
        f_res = food.match_services({"service_category": "Food & Ration Entitlements"})
        assert len(f_res) > 0
    finally:
        if old_gemini:
            os.environ["GEMINI_API_KEY"] = old_gemini
        if old_openai:
            os.environ["OPENAI_API_KEY"] = old_openai


def test_all_pages_import_cleanly():
    """
    INTEGRATION TEST 5: Verifies that app, pages, and components import without syntax or import errors.
    """
    import app
    from pages import healthcare, education, food_services
    from components import navigation, chat_interface, scheme_cards, hospital_map, application_guide

    assert callable(healthcare.render_healthcare_page)
    assert callable(education.render_education_page)
    assert callable(food_services.render_food_services_page)
    assert callable(navigation.render_header)
