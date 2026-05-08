"""
HTTP Translation routes (stateless, for testing / batch use)
POST /translate/sign    → keypoints → French text
POST /translate/text    → French text → simplified + LSF keywords
"""

from fastapi import APIRouter
from models.schemas import KeypointPayload, TranslationResult, RecruiterMessage
from services.sign_language import SignLanguageService
from services.nlp import NLPService

router = APIRouter(prefix="/translate", tags=["translation"])

_sign_svc = SignLanguageService()
_nlp_svc = NLPService()


@router.post("/sign", response_model=TranslationResult)
async def translate_sign(payload: KeypointPayload):
    result = _sign_svc.translate({"keypoints": payload.keypoints})
    return TranslationResult(
        sign=result.sign,
        text=result.text,
        confidence=result.confidence,
        latency_ms=result.latency_ms,
    )


@router.post("/text", response_model=RecruiterMessage)
async def translate_text(body: dict):
    text = body.get("text", "")
    result = _nlp_svc.process_recruiter_message(text)
    return RecruiterMessage(
        text=result.original,
        simplified_text=result.simplified,
        sign_keywords=result.sign_keywords,
    )
