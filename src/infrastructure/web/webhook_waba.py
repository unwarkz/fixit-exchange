import os, hmac, hashlib
from fastapi import APIRouter, Request, HTTPException
from src.domain.entities import DomainEvent, User, EventType
from src.application.use_cases.process_event import ProcessEvent
from src.infrastructure.adapters.whatsapp_api import WhatsAppSender
from src.infrastructure.adapters.sqlite_repo import SQLiteDialogRepo
from src.infrastructure.adapters.okdesk_api import OkdeskIssueCreator
from src.config import logger

router = APIRouter()

def verify_signature(secret: str, payload: bytes, header: str) -> bool:
    if not header or not header.startswith('sha256='):
        return False
    received = header.split('=', 1)[1]
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(received, expected)

@router.post("/webhook/waba")
async def waba_hook(request: Request):
    body = await request.body()
    sig = request.headers.get("X-Hub-Signature-256")
    secret = os.getenv("WABA_APP_SECRET", "")
    if not verify_signature(secret, body, sig):
        logger.error("Invalid WhatsApp signature")
        raise HTTPException(status_code=401, detail="Invalid signature")
    data = await request.json()
    contact = data['entry'][0]['changes'][0]['value']['contacts'][0]
    message = data['entry'][0]['changes'][0]['value']['messages'][0]
    user = User(id=contact['wa_id'], name=contact['profile']['name'])
    event = DomainEvent(type=EventType.MESSAGE, payload={"text": message['text']['body']})
    processor = ProcessEvent(WhatsAppSender(), SQLiteDialogRepo(), OkdeskIssueCreator())
    await processor.handle(user, event)
    return {"status": "ok"}
