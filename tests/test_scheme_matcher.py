"""
Unit tests for SchemeMatcher service.
Covers real dataset loading, ranking, and Test 4 (Safe fallback when no match is found).
"""

import pytest
import os
from services.scheme_matcher import SchemeMatcher
from services.eligibility_engine import MatchCategory


@pytest.fixture
def matcher():
    return SchemeMatcher()


def test_real_dataset_loads_ten_schemes(matcher):
    schemes = matcher.load_schemes()
    assert len(schemes) >= 10
    scheme_ids = [s["scheme_id"] for s in schemes]
    assert "SCHEME-AB-PMJAY" in scheme_ids
    assert "SCHEME-AB-ARK" in scheme_ids
    assert "SCHEME-YESHASVINI" in scheme_ids


def test_ranking_and_potential_match(matcher):
    user_profile = {
        "state": "Karnataka",
        "city": "Bengaluru",
        "condition": "cardiac",
        "ration_card_type": "BPL"
    }

    results = matcher.match_schemes(user_profile)
    assert len(results) > 0
    top = results[0]
    # Top scheme should be a strong match (AB-PMJAY or AB-ArK)
    assert top.match_category in [MatchCategory.NO_KNOWN_CONFLICT, MatchCategory.POTENTIALLY_RELEVANT]
    assert top.rank_score > 0


def test_no_match_found_safe_fallback(matcher):
    """
    TEST 4: Out-of-scope profile where rules do not identify a match.
    Expected: Does NOT crash, explains why or returns non-matches without claiming no assistance exists anywhere.
    """
    user_profile = {
        "state": "NonExistentStateXYZ",
        "condition": "unrelated_rare_symptom_not_in_db",
        "ration_card_type": "None",
        "annual_income": 9999999
    }

    results = matcher.match_schemes(user_profile)
    assert len(results) > 0

    actionable = matcher.get_actionable_matches(user_profile)
    # Actionable matches will be empty or require verification
    for r in results:
        # Check that none of them falsely claim guaranteed eligibility
        assert r.match_category != MatchCategory.NO_KNOWN_CONFLICT


def test_missing_json_file_resilience():
    """
    TEST 6: Gracefully handles missing JSON file without raising unhandled exception.
    """
    non_existent_matcher = SchemeMatcher(data_path="data/non_existent_file.json")
    schemes = non_existent_matcher.load_schemes()
    assert schemes == []
    results = non_existent_matcher.match_schemes({"state": "Karnataka"})
    assert results == []
