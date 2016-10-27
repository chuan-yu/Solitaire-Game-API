from protorpc import messages
from card_forms import CardForms

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    moves = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    piles = messages.MessageField(CardForms, 5, repeated=True)
    foundations = messages.MessageField(CardForms, 6, repeated=True)
    deck = messages.MessageField(CardForms, 7, required=True)
    open_deck = messages.MessageField(CardForms, 8, required=True)
    message = messages.StringField(9, required=True)


class GameForms(messages.Message):
    """Return multiple GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)