from src.application.ports.accounting_connector import IAccountingConnector
from src.config import logger

class OneCConnector(IAccountingConnector):
    async def fetch_payment_statuses(self):
        logger.debug("Stub: fetch_payment_statuses called")
        return []

    async def send_issue_update(self, updates):
        logger.debug(f"Stub: send_issue_update with {updates}")
