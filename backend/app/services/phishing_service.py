"""Phishing and email security analysis service."""

from dataclasses import dataclass, field
import re
from typing import Any
from urllib.parse import urlparse

SUSPICIOUS_TLDS = {".xyz", ".top", ".click", ".buzz", ".monster", ".work", ".fit", ".rest"}

URGENT_CREDENTIAL_PHRASES = [
    r"\bverify your account\b",
    r"\bconfirm your password\b",
    r"\baccount suspended\b",
    r"\bsecurity alert\b.*\blogin\b",
    r"\bunauthorized access detected\b",
    r"\bupdate your billing\b",
    r"\bimmediate action required\b",
    r"\bwire transfer\b",
    r"\bclaim your prize\b",
    r"\bwon the lottery\b",
    r"\bcrypto transfer\b",
    r"\breset password immediately\b",
    r"\benter your (ssn|credit card|credentials|bank)\b",
]

# brand keyword -> domains that legitimately send mail for that brand
BRAND_DOMAINS: dict[str, tuple[str, ...]] = {
    "paypal": ("paypal.com",),
    "google": ("google.com", "gmail.com", "googlemail.com"),
    "microsoft": ("microsoft.com", "outlook.com", "live.com"),
    "apple": ("apple.com", "icloud.com"),
    "netflix": ("netflix.com",),
    "amazon": ("amazon.com", "amazon.in", "amazon.co.uk"),
    "bank of america": ("bankofamerica.com",),
    "chase": ("chase.com",),
    "wells fargo": ("wellsfargo.com",),
}


def _sender_domain(address: str) -> str:
    """Return the lowercase domain part of an email address ('' if there is none)."""
    if "@" not in address:
        return ""
    return address.rsplit("@", 1)[-1].strip(" <>").lower()


def _domain_matches(domain: str, legit_domains: tuple[str, ...]) -> bool:
    """True only for the exact domain or a real subdomain of it.

    'mail.paypal.com' matches 'paypal.com'.
    'paypal.com.evil.xyz' and 'evil-paypal.com' do NOT.
    """
    return any(domain == d or domain.endswith("." + d) for d in legit_domains)


def _mentions(text: str, word: str) -> bool:
    """Whole-word match, so 'purchase' does not count as 'chase'."""
    return re.search(rf"\b{re.escape(word)}\b", text) is not None


@dataclass
class PhishingAnalysisResult:
    """Analysis result describing email phishing risk and specific reasons."""

    risk_level: str  # none | low | medium | high
    reasons: list[str] = field(default_factory=list)
    confidence: float = 0.0


def analyze_phishing(email_data: dict[str, Any]) -> PhishingAnalysisResult:
    """Analyze email metadata and content for phishing indicators.

    Produces explainable security warnings and calculates risk level.
    """
    reasons: list[str] = []
    sender_email = (email_data.get("sender_email") or "").lower().strip()
    sender_name = (email_data.get("sender_name") or "").lower().strip()
    subject = (email_data.get("subject") or "").lower()
    body_text = (email_data.get("body_text") or "").lower()
    body_html = (email_data.get("body_html") or "").lower()

    content = f"{subject}\n{body_text}"

    # 1. Brand Spoofing Check: display name (or an urgent subject) names a brand,
    #    but the sender's real domain is not that brand's domain
    sender_domain = _sender_domain(sender_email)
    has_urgent_phrase = any(re.search(p, content) for p in URGENT_CREDENTIAL_PHRASES)
    for brand, legit_domains in BRAND_DOMAINS.items():
        in_name = _mentions(sender_name, brand)
        in_subject = _mentions(subject, brand)
        if not (in_name or (in_subject and has_urgent_phrase)):
            continue
        if sender_domain and not _domain_matches(sender_domain, legit_domains):
            reasons.append(
                f"Sender display name mentions '{brand.title()}' but sender address ({sender_email}) is from an unrelated domain."
            )

    # 2. Urgent Credential / Account Suspension phrases
    found_phrases = []
    for pattern in URGENT_CREDENTIAL_PHRASES:
        if re.search(pattern, content):
            matched = pattern.replace(r"\b", "").replace(".*", "...")
            found_phrases.append(matched)

    if found_phrases:
        reasons.append(
            f"Contains high-urgency security or credential phrasing: {', '.join(found_phrases[:3])}."
        )

    # 3. URL Analysis
    urls = re.findall(r'https?://[^\s<>"\']+', content + " " + body_html)
    ip_in_url = False
    suspicious_tld_found = False

    for url in urls:
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname or ""
            # Check for IP address as hostname
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname):
                ip_in_url = True
            # Check for suspicious top-level domains
            for tld in SUSPICIOUS_TLDS:
                if hostname.endswith(tld):
                    suspicious_tld_found = True
        except Exception:
            continue

    if ip_in_url:
        reasons.append("Contains link(s) pointing directly to a raw numerical IP address instead of a domain.")

    if suspicious_tld_found:
        reasons.append("Contains links hosted on top-level domains frequently associated with phishing or malware.")

    # 4. Mismatched Reply-To
    reply_to = (email_data.get("reply_to") or "").lower().strip()
    if reply_to and sender_email and reply_to != sender_email:
        sender_domain = sender_email.split("@")[-1] if "@" in sender_email else ""
        reply_domain = reply_to.split("@")[-1] if "@" in reply_to else ""
        if sender_domain and reply_domain and sender_domain != reply_domain:
            reasons.append(
                f"Reply-To address domain ({reply_domain}) does not match sender domain ({sender_domain})."
            )

    # Calculate overall risk
    num_issues = len(reasons)
    if num_issues == 0:
        return PhishingAnalysisResult(risk_level="none", reasons=[], confidence=0.95)
    elif num_issues == 1:
        return PhishingAnalysisResult(risk_level="low", reasons=reasons, confidence=0.75)
    elif num_issues == 2:
        return PhishingAnalysisResult(risk_level="medium", reasons=reasons, confidence=0.88)
    else:
        return PhishingAnalysisResult(risk_level="high", reasons=reasons, confidence=0.96)
