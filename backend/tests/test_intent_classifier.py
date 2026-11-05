"""
Tests for conversational intent classification and escalation detection.
"""

from app.ai.intent_classifier import IntentClassifier
from app.ai.providers.mock import MockAIProvider
from app.ai.schemas import MessageIntent
from app.models.enums import AccountType


def test_classify_greeting() -> None:
    """Classify greeting intent."""
    classifier = IntentClassifier(MockAIProvider())
    result = classifier.classify("Hello there!", account_type=AccountType.BUSINESS)

    assert result.intent == MessageIntent.GREETING
    assert result.requires_human is False


def test_classify_pricing_enquiry() -> None:
    """Classify pricing enquiries for business account."""
    classifier = IntentClassifier(MockAIProvider())
    result = classifier.classify("How much do you charge for bottle ads?", account_type=AccountType.BUSINESS)

    assert result.intent == MessageIntent.PRICING_ENQUIRY
    assert result.requires_human is False


def test_classify_complaint_escalation() -> None:
    """Complaints must automatically trigger human review."""
    classifier = IntentClassifier(MockAIProvider())
    result = classifier.classify("This is the worst service, broken bottles delivered!", account_type=AccountType.BUSINESS)

    assert result.intent == MessageIntent.COMPLAINT
    assert result.requires_human is True


def test_classify_negotiation_escalation() -> None:
    """Price negotiation requests require human approval."""
    classifier = IntentClassifier(MockAIProvider())
    result = classifier.classify("Can you give me a 50% discount on 10,000 bottles?", account_type=AccountType.BUSINESS)

    assert result.intent == MessageIntent.NEGOTIATION
    assert result.requires_human is True


def test_classify_emergency_sensitive_escalation() -> None:
    """Emergency or legal messages require human review."""
    classifier = IntentClassifier(MockAIProvider())
    result = classifier.classify("Emergency hospital situation", account_type=AccountType.PERSONAL)

    assert result.intent == MessageIntent.SENSITIVE_CONVERSATION
    assert result.requires_human is True
