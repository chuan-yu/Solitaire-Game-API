from protorpc import messages

class StringMessage(messages.Message):
    """Outbound message"""
    message = messages.StringField(1, required=True)