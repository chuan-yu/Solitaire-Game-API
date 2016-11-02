from card_forms import CardForm, CardForms


def card_deck_objects_to_message_field(objects):
    """Conver Python card deck objects to MessageField"""
    if type(objects) is not list:
        objects = [objects]

    decks = []
    for p in objects:
        cards = []
        if p["cards"] != []:
            for c in p["cards"]:
                card = CardForm(suit=c['suit'],
                                number=c['number'],
                                color=c['color'],
                                upturned=c['upturned'])
                cards.append(card)
        deck = CardForms(cards=cards)
        decks.append(deck)

    if len(decks) == 1:
        return decks[0]
    else:
        return decks


def byteify(input):
    """Convert JSON string to JSON object"""
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input
