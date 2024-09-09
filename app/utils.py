from enum import Enum


class TransactionType(str, Enum):
    RETURN = 'return'
    ISSUE = 'issue'
