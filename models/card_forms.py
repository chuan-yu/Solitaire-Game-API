from protorpc import messages


class CardForm(messages.Message):
    """CardForm for Card MessageField"""
    suit = messages.StringField(1, required=True)
    number = messages.IntegerField(2, required=True)
    color = messages.StringField(3, required=True)
    upturned = messages.BooleanField(4, required=True)


class CardForms(messages.Message):
    """Return multiple CardForms"""
    cards = messages.MessageField(CardForm, 2, repeated=True)
