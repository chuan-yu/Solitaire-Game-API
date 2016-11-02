from protorpc import messages
from card_forms import CardForms


class GameHistoryForm(messages.Message):
    """Return the form representation of the Game History"""
    sequence = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    piles = messages.MessageField(CardForms, 4, repeated=True)
    foundations = messages.MessageField(CardForms, 5, repeated=True)
    deck = messages.MessageField(CardForms, 6, required=True)
    open_deck = messages.MessageField(CardForms, 7, required=True)


class GameHistoryForms(messages.Message):
    """Return multiple GameHistory Form"""
    items = messages.MessageField(GameHistoryForm, 1, repeated=True)
