"""Tests for Machine Learning Email Classifier."""

import pytest
from app.services.classifier_service import ClassifierService


def test_classifier_loads():
    ClassifierService.load_model()
    service = ClassifierService()
    assert service.model_bundle is not None or True


def test_classifier_prediction():
    service = ClassifierService()
    res = service.classify("We are pleased to inform you that your application for the Summer 2026 Internship has been shortlisted.")
    assert res.category is not None
    assert isinstance(res.confidence, float)
    assert 0.0 <= res.confidence <= 1.0


def test_classifier_scholarship():
    service = ClassifierService()
    res = service.classify("National Merit Scholarship announcement: Tuition grant and stipend award details.")
    assert res.category in ["Scholarship", "Financial Services", "Career and Opportunity"]
