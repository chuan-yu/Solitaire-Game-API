from protorpc import messages


class NewGameForm(messages.Message):
    """Form used to send a new game request"""
    user_name = messages.StringField(1, required=True)
