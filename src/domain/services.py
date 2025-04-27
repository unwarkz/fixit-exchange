from typing import List
from src.domain.flows.simple_lead_flow import FLOW_RULES
from src.domain.entities import DomainEvent, DialogAction, Dialog

class FlowRule:
    def __init__(self, state, predicate, next_state, actions):
        self.state = state
        self.predicate = predicate
        self.next_state = next_state
        self.actions = actions

class FlowEngine:
    def __init__(self, rules: List[FlowRule]):
        self._rules_by_state = {}
        for rule in rules:
            self._rules_by_state.setdefault(rule.state, []).append(rule)

    def start_new_dialog(self, user):
        return Dialog(user_id=user.id, state=list(self._rules_by_state.keys())[0], context={})

    def next(self, dialog: Dialog, event: DomainEvent) -> List[DialogAction]:
        for rule in self._rules_by_state.get(dialog.state, []):
            if rule.predicate(event):
                dialog.state = rule.next_state
                return [act.with_context(dialog.context) for act in rule.actions]
        return []
