from src.application.ports.message_sender import IMessageSender
from src.application.ports.dialog_repo import IDialogRepository
from src.application.ports.issue_creator import IIssueCreator
from src.domain.services import FlowEngine
from src.domain.entities import DomainEvent, User
from src.domain.flows.simple_lead_flow import FLOW_RULES

class ProcessEvent:
    def __init__(
        self,
        sender: IMessageSender,
        repo: IDialogRepository,
        issue_creator: IIssueCreator,
    ):
        self._engine = FlowEngine(FLOW_RULES)
        self._sender = sender
        self._repo   = repo
        self._issue  = issue_creator

    async def handle(self, user: User, event: DomainEvent):
        dialog = self._repo.get(user.id) or self._engine.start_new_dialog(user)
        actions = self._engine.next(dialog, event)
        self._repo.save(dialog)

        for action in actions:
            if action.type == "reply":
                await self._sender.send(user.id, action.text)
            elif action.type == "create_issue":
                await self._issue.create("okdesk", action.issue)
