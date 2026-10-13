"""
Unit tests for LifeBridge Eligibility Engine.
Covers Test 1 (Potential Match), Test 2 (Missing Information),
Test 3 (Confirmed Unmet Requirement), and Test 6 (Missing Data Resilience).
"""

import pytest
from services.eligibility_engine import EligibilityEngine, MatchCategory


@pytest.fixture
def engine():
    return EligibilityEngine()


@pytest.fixture
def sample_pmjay_scheme():
    return {
        "scheme_id": "SCHEME-AB-PMJAY",
        "scheme_name": "Ayushman Bharat - PM-JAY",
        "eligibility_rules": {
            "supported_states": ["All", "Karnataka"],
            "supported_conditions": ["cancer", "cardiac", "kidney", "surgery"],
            "income_limit_annual": None,
            "requires_bpl_or_card": True,
            "requires_ration_card": True
        }
    }


@pytest.fixture
def sample_hmdg_scheme():
    return {
        "scheme_id": "SCHEME-HMDG",
        "scheme_name": "Health Minister's Discretionary Grant",
        "eligibility_rules": {
            "supported_states": ["All", "Karnataka"],
            "supported_conditions": ["cancer", "cardiac", "kidney"],
            "income_limit_annual": 125000,
            "requires_bpl_or_card": False
        }
    }


def test_potential_scheme_match(engine, sample_pmjay_scheme):
    """
    TEST 1: User provides sufficient details matching conditions and location.
    Must return matching reasons without claiming guaranteed approval.
    """
    user_profile = {
        "state": "Karnataka",
        "condition": "cancer",
        "ration_card_type": "BPL"
    }

    result = engine.evaluate_scheme(sample_pmjay_scheme, user_profile)

    assert result.match_category in [MatchCategory.NO_KNOWN_CONFLICT, MatchCategory.POTENTIALLY_RELEVANT]
    assert len(result.reasons) > 0
    assert any("Geographic" in r for r in result.reasons)
    assert any("Medical" in r for r in result.reasons)
    assert any("Beneficiary" in r for r in result.reasons)
    # Ensure official verification disclaimer is present
    assert any("Final eligibility determination" in v for v in result.official_verification_items)


def test_missing_information_requests(engine, sample_pmjay_scheme):
    """
    TEST 2: Missing mandatory information does NOT reject user, but marks missing info.
    """
    user_profile = {
        "state": "Karnataka",
        "condition": "cancer"
        # Ration card not provided
    }

    result = engine.evaluate_scheme(sample_pmjay_scheme, user_profile)

    assert result.match_category == MatchCategory.POTENTIALLY_RELEVANT
    assert len(result.missing_information) > 0
    assert any("Ration card" in m for m in result.missing_information)
    assert len(result.unmet_criteria) == 0  # Not rejected


def test_confirmed_unmet_requirement(engine, sample_hmdg_scheme):
    """
    TEST 3: Confirmed unmet criterion explains reason and does not mark as match.
    """
    user_profile = {
        "state": "Karnataka",
        "condition": "cancer",
        "annual_income": 350000  # Exceeds 125,000 threshold
    }

    result = engine.evaluate_scheme(sample_hmdg_scheme, user_profile)

    assert result.match_category == MatchCategory.KNOWN_REQUIREMENT_NOT_MET
    assert len(result.unmet_criteria) > 0
    assert any("Income ceiling exceeded" in u for u in result.unmet_criteria)
    assert result.rank_score == 0


def test_missing_data_resilience(engine):
    """
    TEST 6: Handles missing optional fields in scheme record without crashing.
    """
    corrupt_scheme = {
        "scheme_id": "TEST-MINIMAL"
        # Missing eligibility_rules, missing scheme_name, missing supported_conditions
    }
    user_profile = {"state": "Karnataka"}

    result = engine.evaluate_scheme(corrupt_scheme, user_profile)

    assert result is not None
    assert result.scheme.get("scheme_id") == "TEST-MINIMAL"
    assert isinstance(result.missing_information, list)
