import os
import httpx
import hmac, hashlib
from src.application.ports.message_sender import IMessageSender
from src.config import logger

WABA_TOKEN = os.getenv("WABA_TOKEN")
PHONE_ID   = os.getenv("WABA_PHONE_NUMBER_ID")
API_URL    = f"https://graph.facebook.com/v15.0/{PHONE_ID}/messages"

class WhatsAppSender(IMessageSender):
    async def send(self, to: str, text: str):
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text}
        }
        headers = {"Authorization": f"Bearer {WABA_TOKEN}"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(API_URL, json=payload, headers=headers)
            resp.raise_for_status()
            logger.debug(f"Sent WhatsApp message to {to}: {text}")
