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


def _brand_email(sender_email: str, subject: str = "Account notice", name: str = "PayPal Support") -> dict:
    return {
        "subject": subject,
        "sender_name": name,
        "sender_email": sender_email,
        "body_text": "Please log in to review your account.",
    }


def test_phishing_lookalike_domains_containing_brand_are_flagged():
    # The real domain is *.xyz / evil-paypal.com, not paypal.com
    for sender in ["help@paypal.com.secure-login.xyz", "help@evil-paypal.com"]:
        res = analyze_phishing(_brand_email(sender))
        assert res.risk_level != "none", sender


def test_phishing_real_brand_subdomain_is_not_flagged():
    res = analyze_phishing(_brand_email("service@mail.paypal.com"))
    assert res.risk_level == "none"


def test_phishing_brand_inside_another_word_is_not_flagged():
    # "purchase" contains "chase", but it is not the bank
    res = analyze_phishing(_brand_email("orders@localstore.com", subject="Your purchase receipt", name="Local Store"))
    assert res.risk_level == "none"
