"""
Tests for the ClaimProcessor class.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import pytest
from campusfinder import ClaimProcessor


@pytest.fixture
def processor():
    return ClaimProcessor()


def test_register_claim(processor):
    claim = processor.register_claim("c1", "item1", "user1", "This is my phone, black iPhone 15")
    assert claim["status"] == "pending"
    assert claim["priority"] > 0


def test_get_claim(processor):
    processor.register_claim("c1", "item1", "user1", "Description here")
    assert processor.get_claim("c1") is not None
    assert processor.get_claim("c999") is None


def test_compute_priority_with_evidence(processor):
    claim = processor.register_claim("c1", "item1", "user1",
                                     "This is definitely my phone, I can prove it.",
                                     evidence="IMEI: 123456789012345")
    assert claim["priority"] > 30  # should get evidence + description + timeliness


def test_compute_priority_without_evidence(processor):
    claim = processor.register_claim("c2", "item2", "user2", "Short desc")
    # No evidence, short description
    assert claim["priority"] <= 50


def test_approve_claim(processor):
    processor.register_claim("c1", "item1", "user1", "My phone description here")
    updated = processor.approve_claim("c1")
    assert updated["status"] == "approved"


def test_reject_claim(processor):
    processor.register_claim("c1", "item1", "user1", "My phone description here")
    updated = processor.reject_claim("c1")
    assert updated["status"] == "rejected"


def test_withdraw_claim(processor):
    processor.register_claim("c1", "item1", "user1", "My phone description here")
    updated = processor.withdraw_claim("c1")
    assert updated["status"] == "withdrawn"


def test_invalid_transition(processor):
    processor.register_claim("c1", "item1", "user1", "My phone description here")
    processor.reject_claim("c1")
    with pytest.raises(ValueError):
        processor.approve_claim("c1")  # rejected -> approved is not allowed


def test_claim_not_found_transition(processor):
    with pytest.raises(KeyError):
        processor.transition_status("nonexistent", "approved")


def test_get_claims_for_item(processor):
    processor.register_claim("c1", "item1", "user1", "Claim one with enough description text")
    processor.register_claim("c2", "item1", "user2", "Claim two with sufficient detail provided",
                             evidence="Photo proof attached here")
    claims = processor.get_claims_for_item("item1")
    assert len(claims) == 2
    # Higher priority claim should come first
    assert claims[0]["priority"] >= claims[1]["priority"]


def test_get_pending_claims(processor):
    processor.register_claim("c1", "item1", "user1", "Pending claim description")
    processor.register_claim("c2", "item2", "user2", "Another pending claim")
    processor.approve_claim("c1")
    pending = processor.get_pending_claims()
    assert len(pending) == 1
    assert pending[0]["claim_id"] == "c2"


def test_validate_claim_valid(processor):
    valid, errors = processor.validate_claim({
        "description": "This is a valid claim description",
        "item_id": "item1",
        "claimant_id": "user1",
    })
    assert valid is True
    assert errors == []


def test_validate_claim_invalid(processor):
    valid, errors = processor.validate_claim({"description": "short"})
    assert valid is False
    assert len(errors) >= 1


def test_audit_log(processor):
    processor.register_claim("c1", "item1", "user1", "Test claim for audit")
    processor.approve_claim("c1")
    log = processor.get_audit_log("c1")
    assert len(log) == 2
    assert log[0]["action"] == "registered"
