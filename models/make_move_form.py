from protorpc import messages


class Action(messages.Enum):
    """Enum class for action"""
    MOVE = 1
    DEAL = 2
    SHOW = 3


class StackName(messages.Enum):
    """Enum class for stack name"""
    DECK = 1
    FOUNDATION_0 = 2
    FOUNDATION_1 = 3
    FOUNDATION_2 = 4
    FOUNDATION_3 = 5
    PILE_0 = 6
    PILE_1 = 7
    PILE_2 = 8
    PILE_3 = 9
    PILE_4 = 10
    PILE_5 = 11
    PILE_6 = 12


class MakeMoveForm(messages.Message):
    """Form used to submit a make a move request"""
    action = messages.EnumField('Action', 1, default='DEAL', required=True)
    origin = messages.EnumField('StackName', 2)
    destination = messages.EnumField('StackName', 3)
    card_position = messages.IntegerField(4)
