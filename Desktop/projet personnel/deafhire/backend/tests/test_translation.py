"""Translation / sign language service tests."""

import pytest
from services.sign_language import SignLanguageService, asl_to_french, sign_to_sentence, SignResult


def test_asl_to_french_known():
    assert asl_to_french("hello") == "Bonjour"
    assert asl_to_french("thank you") == "Merci"
    assert asl_to_french("yes") == "Oui"
    assert asl_to_french("work") == "Travail"


def test_asl_to_french_case_insensitive():
    assert asl_to_french("HELLO") == "Bonjour"
    assert asl_to_french("Hello") == "Bonjour"


def test_asl_to_french_unknown_passthrough():
    assert asl_to_french("unknown_sign_xyz") == "unknown_sign_xyz"


def test_sign_to_sentence_known():
    sentence = sign_to_sentence("Bonjour")
    assert "Bonjour" in sentence


def test_sign_to_sentence_fallback():
    sentence = sign_to_sentence("SomeUnknownLabel")
    assert "SomeUnknownLabel" in sentence


def test_service_translate_returns_sign_result():
    svc = SignLanguageService()
    result = svc.translate({"sign": "hello", "confidence": 0.9})
    assert isinstance(result, SignResult)
    assert result.sign == "Bonjour"
    assert result.confidence == pytest.approx(0.9)
    assert isinstance(result.text, str)
    assert len(result.text) > 0
    assert result.latency_ms >= 0


def test_service_translate_empty_sign():
    svc = SignLanguageService()
    result = svc.translate({"sign": "", "confidence": 0.5})
    assert isinstance(result, SignResult)
    assert result.sign == "Neutre"


def test_translation_endpoint(client):
    resp = client.post("/translate", json={"sign": "hello", "confidence": 0.85})
    assert resp.status_code == 200
    data = resp.json()
    assert "sign" in data
    assert "text" in data
