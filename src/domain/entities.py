from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict

class EventType(Enum):
    MESSAGE = "message"
    ISSUE_UPDATED = "issue_updated"
    PAYMENT = "payment"

@dataclass
class DomainEvent:
    type: EventType
    payload: Dict[str, Any]

@dataclass
class User:
    id: str
    name: str = ""

@dataclass
class Message:
    from_id: str
    text: str

@dataclass
class Issue:
    title: str
    description: str

@dataclass
class DialogAction:
    type: str  # 'reply' | 'create_issue'
    text: str = ""
    issue: Issue = None

    def with_context(self, ctx: Dict[str, Any]):
        rendered_text = self.text.format(**ctx)
        rendered_issue = None
        if self.issue:
            title = self.issue.title.format(**ctx)
            description = self.issue.description.format(**ctx)
            rendered_issue = Issue(title=title, description=description)
        return DialogAction(type=self.type, text=rendered_text, issue=rendered_issue)

@dataclass
class Dialog:
    user_id: str
    state: str
    context: Dict[str, Any] = field(default_factory=dict)
