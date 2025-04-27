import os, base64
from fastapi import APIRouter, Request, HTTPException
from src.domain.entities import DomainEvent, User, EventType
from src.application.use_cases.process_event import ProcessEvent
from src.infrastructure.adapters.whatsapp_api import WhatsAppSender
from src.infrastructure.adapters.sqlite_repo import SQLiteDialogRepo
from src.infrastructure.adapters.okdesk_api import OkdeskIssueCreator
from src.config import logger

router = APIRouter()

def verify_basic_auth(header: str):
    if not header or not header.startswith("Basic "):
        return False
    creds = base64.b64decode(header.split(" ",1)[1]).decode()
    user, pwd = creds.split(":",1)
    return user == os.getenv("OKDESK_USER") and pwd == os.getenv("OKDESK_PASS")

@router.post("/webhook/okdesk")
async def okdesk_hook(request: Request):
    auth = request.headers.get("Authorization", "")
    if not verify_basic_auth(auth):
        logger.error("Invalid Okdesk auth")
        raise HTTPException(status_code=401, detail="Unauthorized")
    data = await request.json()
    ticket = data.get("ticket", {})
    user_id = ""  # lookup by ticket ID if stored
    user = User(id=user_id)
    event = DomainEvent(type=EventType.ISSUE_UPDATED, payload={"status": ticket.get("status"), "id": ticket.get("id")})
    processor = ProcessEvent(WhatsAppSender(), SQLiteDialogRepo(), OkdeskIssueCreator())
    await processor.handle(user, event)
    return {"status": "ok"}
