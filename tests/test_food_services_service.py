"""
Unit tests for Food & Essential Services Service.
Verifies new card applications, ONORC portability, entitlement inquiries,
state-specific filtering, unknown eligibility handling, nearby centre search,
and JSON resilience.
"""

import pytest
from services.food_services_service import FoodServicesService


@pytest.fixture
def service():
    return FoodServicesService()


def test_real_dataset_loads_ten_food_services(service):
    services = service.load_services()
    assert len(services) >= 10
    ids = [s["service_id"] for s in services]
    assert "FOOD-NFSA-PHH" in ids
    assert "FOOD-ONORC" in ids
    assert "FOOD-KA-NEW-RC" in ids
    assert "FOOD-KA-ANNA-BHAGYA" in ids
    assert "FOOD-KA-FPS-LOCATOR" in ids


def test_new_ration_card_applicant_receives_application_service(service):
    """
    TEST 1: A new ration-card applicant receives relevant application information.
    """
    profile = {
        "service_category": "Apply for New Ration Card",
        "has_existing_card": False,
        "state": "Karnataka"
    }

    matches = service.get_actionable_matches(profile)
    assert len(matches) > 0
    top = matches[0]
    assert top.service["service_id"] == "FOOD-KA-NEW-RC"
    assert "Application" in top.service["name"]
    assert "ahara.kar.nic.in" in top.service["official_application_url"]


def test_portability_inquiry_receives_onorc_info(service):
    """
    TEST 2: A user who already has a ration card and asks about portability receives ONORC.
    """
    profile = {
        "service_category": "Check Portability (One Nation One Ration Card)",
        "has_existing_card": True,
        "state": "Karnataka"
    }

    matches = service.get_actionable_matches(profile)
    assert len(matches) > 0
    top = matches[0]
    assert top.service["service_id"] == "FOOD-ONORC"
    assert "One Nation One Ration Card" in top.service["name"]


def test_entitlement_inquiry_not_forced_through_application(service):
    """
    TEST 3: A user asking only about food entitlements receives entitlement info
    without new-card application being forced on them.
    """
    profile = {
        "service_category": "Food & Ration Entitlements",
        "has_existing_card": True,
        "state": "Karnataka"
    }

    matches = service.get_actionable_matches(profile)
    assert len(matches) > 0
    match_ids = [m.service["service_id"] for m in matches]
    assert "FOOD-KA-ANNA-BHAGYA" in match_ids or "FOOD-PMGKAY" in match_ids


def test_state_specific_services_guard_geography(service):
    """
    TEST 4: State-specific services are not presented as universally available.
    """
    profile = {
        "service_category": "Apply for New Ration Card",
        "state": "Delhi",
        "has_existing_card": False
    }

    all_results = service.match_services(profile)
    ka_service = next((r for r in all_results if r.service["service_id"] == "FOOD-KA-NEW-RC"), None)

    assert ka_service is not None
    assert ka_service.status_label == "Not a Match — Mandatory Requirement Not Met"
    assert any("State limitation" in u for u in ka_service.unmet_criteria)


def test_unknown_eligibility_handled_safely(service):
    """
    TEST 5: Unknown eligibility information is handled safely.
    """
    profile = {
        "service_category": "Apply for New Ration Card"
        # State and existing card not provided
    }

    results = service.match_services(profile)
    assert len(results) > 0
    for r in results:
        # None should crash or falsely guarantee approval
        assert r.status_label in ["Potential Match", "Not a Match — Mandatory Requirement Not Met", "Service Information Needs Verification"]


def test_nearby_centre_search_does_not_fabricate_locations(service):
    """
    TEST 6: Nearby-centre search does not fabricate locations when query is outside known data.
    """
    centres = service.search_nearby_centres(locality="UnknownFictionalCity999")
    assert centres == []

    # Verified locality in Bengaluru returns real records
    real_centres = service.search_nearby_centres(locality="Jayanagar")
    assert len(real_centres) > 0
    for c in real_centres:
        assert c["verification_status"] == "VERIFIED"
        assert c["latitude"] is not None and c["longitude"] is not None


def test_missing_json_fields_resilience():
    """
    TEST 7: Missing JSON fields do not crash the service.
    """
    service_bad = FoodServicesService(services_data_path="data/non_existent_file.json")
    assert service_bad.load_services() == []
    assert service_bad.match_services({}) == []
