"""Tests for Priority Scoring Service."""

from app.services.priority_service import score_priority


def test_priority_critical_urgent():
    res = score_priority({
        "subject": "URGENT: Action required due today",
        "body_text": "Please submit your documents before the deadline.",
        "sender_email": "admin@university.edu",
        "category": "Administration",
    })
    assert res.priority in ["critical", "high"]


def test_priority_low_newsletter():
    res = score_priority({
        "subject": "Weekly Newsletter and special offers",
        "body_text": "Click here to unsubscribe from our weekly digest.",
        "sender_email": "news@promotions.com",
        "category": "Miscellaneous",
    })
    assert res.priority in ["low", "medium"]
