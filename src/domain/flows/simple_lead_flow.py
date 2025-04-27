from src.domain.enums import State
from src.domain.entities import DialogAction, Issue, DomainEvent, EventType
from src.domain.services import FlowRule

FLOW_RULES = [
    FlowRule(
        state=State.NEW,
        predicate=lambda ev: ev.type == EventType.MESSAGE,
        next_state=State.ASK_NAME,
        actions=[DialogAction(type="reply", text="Здравствуйте! Как вас зовут?")]
    ),
    FlowRule(
        state=State.ASK_NAME,
        predicate=lambda ev: ev.type == EventType.MESSAGE,
        next_state=State.ASK_COMPANY,
        actions=[DialogAction(type="reply", text="Приятно познакомиться, {text}. В какой компании вы работаете?")]
    ),
    FlowRule(
        state=State.ASK_COMPANY,
        predicate=lambda ev: ev.type == EventType.MESSAGE,
        next_state=State.AWAITING_PAYMENT,
        actions=[
            DialogAction(type="create_issue", issue=Issue(
                title="Новая заявка от {text}",
                description="Пользователь {text} из компании {text} запросил помощь"
            )),
            DialogAction(type="reply", text="Спасибо! Заявка создана. Ожидаем оплату.")
        ]
    ),
    FlowRule(
        state=State.AWAITING_PAYMENT,
        predicate=lambda ev: ev.type == EventType.PAYMENT and ev.payload.get("paid"),
        next_state=State.PAID,
        actions=[DialogAction(type="reply", text="Оплата получена, спасибо!")]
    ),
    FlowRule(
        state=State.PAID,
        predicate=lambda ev: ev.type == EventType.ISSUE_UPDATED and ev.payload.get("status") == "closed",
        next_state=State.DONE,
        actions=[DialogAction(type="reply", text="Ваша заявка выполнена. Благодарим обращение!")]
    ),
]
