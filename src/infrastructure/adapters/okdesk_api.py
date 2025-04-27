import os
import httpx
from src.application.ports.issue_creator import IIssueCreator
from src.config import logger

BASE = os.getenv("OKDESK_URL", "").rstrip("/")
API_KEY = os.getenv("OKDESK_API_KEY")
EMAIL   = os.getenv("OKDESK_EMAIL")

class OkdeskIssueCreator(IIssueCreator):
    async def create(self, system: str, issue):
        url = f"{BASE}/api/v2/issues"
        data = {"ticket": {"theme": issue.title, "text": issue.description}}
        headers = {"Api-Key": API_KEY, "Email": EMAIL}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=data, headers=headers)
            resp.raise_for_status()
            result = resp.json()
            ticket_id = result["response"]["id"]
            logger.debug(f"Created Okdesk ticket {ticket_id}")
            return ticket_id

    async def generate_ticket_link(self, ticket_id: int, contact_id: int) -> str:
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                f"{BASE}/login_link?api_token={API_KEY}",
                json={"user_type": "contact", "user_id": contact_id, "one_time": "true"},
                headers={"Accept": "application/json"}
            )
            token_resp.raise_for_status()
            client_token = token_resp.json().get("token")
        link = f"{BASE}/login?token={client_token}&redirect=/issues/{ticket_id}"
        logger.debug(f"Generated ticket link for {ticket_id}: {link}")
        return link
