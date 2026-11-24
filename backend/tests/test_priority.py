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


def test_priority_example_is_not_exam():
    res = score_priority({
        "subject": "Weekly digest",
        "body_text": "For example, here is a productivity tip.",
        "sender_email": "tips@blog.com",
        "category": "Miscellaneous",
    })
    assert res.priority == "medium"


def test_priority_promo_with_expires_is_low_not_critical():
    res = score_priority({
        "subject": "Flash sale expires tonight! 50% off",
        "body_text": "Unsubscribe anytime.",
        "sender_email": "deals@shop.com",
        "category": "Miscellaneous",
    })
    assert res.priority == "low"


def test_priority_real_deadline_still_critical():
    res = score_priority({
        "subject": "Internship application deadline tomorrow",
        "body_text": "Submit your documents.",
        "sender_email": "hr@company.com",
        "category": "Career and Opportunity",
    })
    assert res.priority == "critical"
