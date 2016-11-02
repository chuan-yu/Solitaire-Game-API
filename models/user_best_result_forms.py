from protorpc import messages


class UserBestResultForm(messages.Message):
    """Form for outbound User best result information"""
    user = messages.StringField(1, required=True)
    least_moves = messages.IntegerField(2, required=True)


class UserBestResultForms(messages.Message):
    """Return multiple UserBestResultForm"""
    items = messages.MessageField(UserBestResultForm, 1, repeated=True)
