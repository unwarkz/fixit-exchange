import pytest
from src.application.use_cases.process_event import ProcessEvent
from src.application.ports.message_sender import IMessageSender
from src.application.ports.dialog_repo import IDialogRepository
from src.application.ports.issue_creator import IIssueCreator
from src.domain.entities import DomainEvent, User
from src.domain.enums import State

class DummySender(IMessageSender):
    async def send(self, to: str, text: str):
        pass

class DummyRepo(IDialogRepository):
    def __init__(self):
        self.store = {}
    def get(self, user_id: str):
        return None
    def save(self, dialog):
        self.store[dialog.user_id] = dialog

class DummyIssue(IIssueCreator):
    async def create(self, system: str, issue):
        return "1"

@pytest.mark.asyncio
async def test_process_event_initial_flow():
    sender = DummySender()
    repo = DummyRepo()
    issue = DummyIssue()
    proc = ProcessEvent(sender, repo, issue)
    user = User(id="u1")
    event = DomainEvent(type=None, payload={})
    # start_new_dialog sets initial state NEW
    await proc.handle(user, event)
    assert repo.store["u1"].state is not None
