"""
Unit tests for ConversationService.
Covers Test 7 (Conversation Continuity / Slot Filling) and dynamic follow-up logic.
"""

import pytest
from services.conversation_service import ConversationService


@pytest.fixture
def conv():
    return ConversationService()


def test_conversation_continuity_and_slot_retention(conv):
    """
    TEST 7: User provides location in message 1 and condition in message 2.
    Expected: Previously collected information is retained during the session.
    """
    profile = {}

    # Turn 1: User mentions location
    profile = conv.extract_entities("I live in Bengaluru, Karnataka.", profile)
    assert profile.get("city") == "Bengaluru"
    assert profile.get("state") == "Karnataka"
    assert profile.get("condition") is None

    # Turn 2: User mentions medical condition in separate message
    profile = conv.extract_entities("My father was diagnosed with lung cancer.", profile)
    # Both location AND condition must be retained
    assert profile.get("city") == "Bengaluru"
    assert profile.get("state") == "Karnataka"
    assert profile.get("condition") == "cancer"

    # Turn 3: User mentions ration card
    profile = conv.extract_entities("We have a BPL ration card.", profile)
    assert profile.get("city") == "Bengaluru"
    assert profile.get("state") == "Karnataka"
    assert profile.get("condition") == "cancer"
    assert profile.get("ration_card_type") == "BPL"


def test_dynamic_follow_up_questions(conv):
    """
    Ensures questions only ask for unprovided fields and explain the rationale.
    """
    profile = {"state": "Karnataka", "city": "Bengaluru"}
    answered = []

    questions = conv.get_dynamic_follow_up_questions(profile, answered)
    assert len(questions) > 0
    # First missing question should be condition
    assert questions[0]["id"] == "condition"
    assert "rationale" in questions[0]

    # If condition is already answered, next question is ration card / income
    profile["condition"] = "cancer"
    questions2 = conv.get_dynamic_follow_up_questions(profile, answered)
    assert questions2[0]["id"] in ["ration_card", "income"]


def test_grounded_faq_responses(conv):
    """
    Ensures questions like 'Which documents do I need?' return grounded information.
    """
    profile = {"state": "Karnataka", "condition": "cancer", "ration_card_type": "BPL"}
    res = conv.handle_user_query("Which documents should I prepare?", profile, active_scheme_id="SCHEME-AB-PMJAY")

    assert res["action"] == "show_documents"
    assert "Aadhaar Card" in res["text"]
    assert "Ration Card" in res["text"]
