"""Smart email priority detection service."""

from dataclasses import dataclass, field
import re
from typing import Any

URGENT_KEYWORDS = [
    "urgent",
    "immediate",
    "deadline",
    "last date",
    "expires",
    "critical",
    "final notice",
    "action required",
    "respond by",
    "due today",
    "overdue",
]

IMPORTANT_KEYWORDS = [
    "interview",
    "placement",
    "offer letter",
    "scholarship",
    "internship",
    "application",
    "selection",
    "merit list",
    "result",
    "admit card",
    "exam",
    "hall ticket",
]

PROMOTIONAL_KEYWORDS = [
    "unsubscribe",
    "newsletter",
    "discount",
    "sale",
    "special offer",
    "buy now",
    "promotional",
]


# Marketing markers that, when in the subject, mean "promo" (checked before urgency)
PROMO_SUBJECT_KEYWORDS = [
    "newsletter",
    "discount",
    "sale",
    "special offer",
    "buy now",
    "promotional",
]


def _has(text: str, keyword: str) -> bool:
    """Whole-word match (plural 's' allowed), so 'example' does not contain 'exam'."""
    return re.search(rf"(?<!\w){re.escape(keyword)}s?(?!\w)", text) is not None


@dataclass
class PriorityResult:
    """Result of email priority scoring."""

    priority: str  # critical | high | medium | low
    reason: str
    signals: list[str] = field(default_factory=list)


def score_priority(email_data: dict[str, Any]) -> PriorityResult:
    """Multi-signal priority scoring algorithm.

    Priority hierarchy:
      critical > high > medium > low
    """
    subject = (email_data.get("subject") or "").lower()
    body = (email_data.get("body_text") or email_data.get("snippet") or "").lower()
    category = email_data.get("category") or ""
    sender = (email_data.get("sender_email") or "").lower()

    signals = []

    # 0. Promotional subject (e.g. "Flash sale expires tonight") is low, not critical,
    #    unless the subject also carries a real career/academic keyword
    promo_kw = next((kw for kw in PROMO_SUBJECT_KEYWORDS if _has(subject, kw)), None)
    if promo_kw and not any(_has(subject, kw) for kw in IMPORTANT_KEYWORDS):
        return PriorityResult(
            priority="low",
            reason="Marketing or promotional email indicators",
            signals=[f"Promotional marker in subject: '{promo_kw}'"],
        )

    # 1. Critical signals
    for kw in URGENT_KEYWORDS:
        if _has(subject, kw):
            signals.append(f"Subject contains urgent keyword: '{kw}'")
            return PriorityResult(
                priority="critical",
                reason=f"Urgent keyword '{kw}' detected in subject line",
                signals=signals,
            )

    # 2. High priority signals
    for kw in IMPORTANT_KEYWORDS:
        if _has(subject, kw) or _has(body[:300], kw):
            signals.append(f"Important keyword found: '{kw}'")

    if category in ["Career and Opportunity", "Scholarship"]:
        signals.append(f"Category '{category}' is prioritized")

    if _has(subject, "exam") or _has(subject, "admit card") or _has(body, "deadline"):
        signals.append("Academic or deadline notice detected")

    if len(signals) >= 1 and any(
        _has(subject, kw) for kw in ["interview", "offer letter", "admit card", "selection"]
    ):
        return PriorityResult(
            priority="high",
            reason="High-priority career or academic event detected",
            signals=signals,
        )

    if signals:
        return PriorityResult(
            priority="high",
            reason="Contains key academic or career milestone indicators",
            signals=signals,
        )

    # 3. Low priority signals
    for kw in PROMOTIONAL_KEYWORDS:
        if _has(subject, kw) or _has(body, kw):
            signals.append(f"Promotional marker found: '{kw}'")
            return PriorityResult(
                priority="low",
                reason="Marketing or promotional email indicators",
                signals=signals,
            )

    # 4. Official domain boost
    if sender.endswith(".edu") or sender.endswith(".ac.in") or sender.endswith(".gov"):
        signals.append("Sender is an official academic/government institution")
        return PriorityResult(
            priority="medium",
            reason="Official institutional correspondence",
            signals=signals,
        )

    # 5. Default
    return PriorityResult(
        priority="medium",
        reason="Standard communication priority",
        signals=["Normal priority message"],
    )
