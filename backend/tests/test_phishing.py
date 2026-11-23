"""Tests for Phishing Detection Service."""

from app.services.phishing_service import analyze_phishing


def test_phishing_spoofed_brand():
    res = analyze_phishing({
        "subject": "PayPal Account Alert: Confirm your password",
        "sender_name": "PayPal Security",
        "sender_email": "security@random-attacker-domain.xyz",
        "body_text": "Your account has been restricted. Please confirm your password immediately at http://192.168.1.1/login.",
    })
    assert res.risk_level in ["medium", "high"]
    assert len(res.reasons) > 0


def test_phishing_legitimate_email():
    res = analyze_phishing({
        "subject": "CS 101 Lecture Notes",
        "sender_name": "Prof. Smith",
        "sender_email": "smith@university.edu",
        "body_text": "Here are the slides from today's lecture on binary search trees.",
    })
    assert res.risk_level in ["none", "low"]
