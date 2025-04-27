from enum import Enum

class State(Enum):
    NEW = "NEW"
    ASK_NAME = "ASK_NAME"
    ASK_COMPANY = "ASK_COMPANY"
    AWAITING_PAYMENT = "AWAITING_PAYMENT"
    PAID = "PAID"
    DONE = "DONE"
