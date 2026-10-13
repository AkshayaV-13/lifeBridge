"""
Integrity and end-to-end guide generation tests for all schemes and hospitals.
"""

import pytest
from services.scheme_matcher import SchemeMatcher
from services.hospital_service import HospitalService
from services.application_guide_service import ApplicationGuideService
from services.conversation_service import ConversationService


def test_all_ten_schemes_generate_guides():
    matcher = SchemeMatcher()
    guide_service = ApplicationGuideService()
    schemes = matcher.load_schemes()
    assert len(schemes) == 10

    test_profile = {
        "state": "Karnataka",
        "city": "Bengaluru",
        "condition": "cancer",
        "ration_card_type": "BPL",
        "annual_income": 90000
    }

    for scheme in schemes:
        s_id = scheme["scheme_id"]
        guide = guide_service.generate_guide(s_id, test_profile)
        assert guide is not None, f"Failed to generate guide for {s_id}"
        # Verify 12 core sections exist and are populated
        assert "relevance_points" in guide
        assert "known_factors" in guide
        assert "missing_factors" in guide
        assert "official_confirmations" in guide
        assert "required_docs" in guide
        assert len(guide["required_docs"]) > 0
        assert "application_venue" in guide
        assert "steps" in guide
        assert len(guide["steps"]) > 0
        assert "official_links" in guide
        assert "empaneled_hospitals" in guide
        assert "tracking_info" in guide
        assert "post_approval" in guide
        assert "grievance_procedure" in guide


def test_conversation_end_to_end_scenarios():
    conv = ConversationService()

    # Scenario A: Cancer in Bengaluru
    prof_a = conv.extract_entities(
        "I have cancer and need treatment, but I cannot afford it. I am looking for government assistance and hospitals near Bengaluru.",
        {}
    )
    assert prof_a["city"] == "Bengaluru"
    assert prof_a["condition"] == "cancer"
    assert prof_a.get("income_category") == "low_income"

    # Scenario B: Heart in Karnataka
    prof_b = conv.extract_entities(
        "My father needs heart treatment. Our family income is low. We live in Karnataka. Can you help us find financial assistance?",
        {}
    )
    assert prof_b["state"] == "Karnataka"
    assert prof_b["condition"] == "cardiac"
    assert prof_b.get("income_category") == "low_income"

    # Scenario C: Dialysis
    prof_c = conv.extract_entities(
        "We need maintenance dialysis every week in Bowring Hospital with our BPL card.",
        {}
    )
    assert prof_c["condition"] == "dialysis"
    assert prof_c["ration_card_type"] == "BPL"
    assert prof_c["treating_hospital_type"] == "government"


def test_all_ten_hospitals_valid_coordinates():
    h_service = HospitalService()
    hospitals = h_service.load_hospitals()
    assert len(hospitals) == 10

    for h in hospitals:
        lat = h.get("latitude")
        lon = h.get("longitude")
        assert lat is not None and isinstance(lat, (int, float))
        assert lon is not None and isinstance(lon, (int, float))
        # Bengaluru latitude is ~12.7 to 13.2, longitude is ~77.4 to 77.8
        assert 12.0 <= lat <= 14.0
        assert 77.0 <= lon <= 78.5
        assert len(h.get("participating_schemes", [])) > 0
