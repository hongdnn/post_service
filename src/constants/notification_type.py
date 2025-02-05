from enum import Enum

class NotificationType(Enum):
    REACTION = 0
    COMMENT = 1
    REPLY_COMMENT = 2
    FOLLOW = 3