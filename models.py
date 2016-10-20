from protorpc import messages
from google.appengine.ext import ndb
import json
# from model_utils import card_deck_objects_to_message_field

class User(ndb.Model):
    user_name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()

def card_deck_objects_to_message_field(objects):
        # if len(objects) == 1:
        #     objects = [objects]
        decks = []
        for p in objects:
            cards = []
            if p['cards'] != []:
                for c in p['cards']:
                    card = CardForm(suit=c['suit'],
                                    number=c['number'],
                                    color=c['color'],
                                    upturned=c['upturned'])
                    cards.append(card)
            deck = CardForms(cards=cards)
            decks.append(deck)
        return decks

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

class Game(ndb.Model):
    moves = ndb.IntegerProperty(required=True)
    game_over = ndb.BooleanProperty(required=True)
    user = ndb.KeyProperty(required=True, kind='User')
    piles = ndb.JsonProperty()
    foundations = ndb.JsonProperty()
    deck = ndb.JsonProperty()
    open_deck = ndb.JsonProperty()

    @classmethod
    def new_game(cls, user, piles, foundations, deck, open_deck):
        game = Game(user=user,
                    moves=0,
                    game_over=False,
                    piles=piles,
                    foundations=foundations,
                    deck=deck,
                    open_deck=open_deck)
        game.put()
        return game

    def to_form(self, message):
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.moves = self.moves
        form.game_over = self.game_over
        form.user_name = self.user.get().user_name
        # form.piles = self.piles.encode('utf-8')
        # form.foundations = self.foundations.encode('utf-8')
        # form.deck = self.deck.encode('utf-8')
        # form.open_deck = self.open_deck.encode('utf-8')
        print 'foundations'
        print byteify(json.loads(self.foundations))
        form.piles = card_deck_objects_to_message_field(byteify(json.loads(self.piles)))
        form.foundations = card_deck_objects_to_message_field(byteify(json.loads(self.foundations)))
        form.deck = card_deck_objects_to_message_field(byteify(self.deck))[0]
        form.open_deck = card_deck_objects_to_message_field(byteify(self.open_decks))[0]
        form.message = message
        return form


class CardForm(messages.Message):
    suit = messages.StringField(1, required=True)
    number = messages.IntegerField(2, required=True)
    color = messages.StringField(3, required=True)
    upturned = messages.BooleanField(4, required=True)

class CardForms(messages.Message):
    name = messages.StringField(1, required=True)
    cards = messages.MessageField(CardForm, 2, repeated=True)

class GameForm(messages.Message):
    urlsafe_key = messages.StringField(1, required=True)
    moves = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    user_name = messages.StringField(4, required=True)
    # piles = messages.StringField(5, required=True)
    # foundations = messages.StringField(6, required=True)
    # deck = messages.StringField(7, required=True)
    # open_deck = messages.StringField(8, required=True)
    piles = messages.MessageField(CardForms, 5, repeated=True)
    foundations = messages.MessageField(CardForms, 6, repeated=True)
    deck = messages.MessageField(CardForms, 7, required=True)
    open_deck = messages.MessageField(CardForms, 8, required=True)
    message = messages.StringField(9, required=True)

class NewGameForm(messages.Message):
    user_name = messages.StringField(1, required=True)

# class MakeMoveForm(messages.Message):
#     class Action(messages.Enum):
#         'MOVE' = 'm'
#         'DEAL' = 'd'
#         'SHOW' = 's'

#     class Stack(messages.Enum):
#         'DECK' = 'd'
#         'FOUNDATION 1' = 'f1'
#         'FOUNDATION 2' = 'f2'
#         'FOUNDATION 3' = 'f3'
#         'FOUNDATION 4' = 'f4'
#         'PILE 0' = 'p0'
#         'PILE 1' = 'p1'
#         'PILE 2' = 'p2'
#         'PILE 3' = 'p3'
#         'PILE 4' = 'p4'
#         'PILE 5' = 'p5'
#         'PILE 6' = 'p6'

#     action = messages.EnumField('MakeMoveForm.Action', 1, default='DEAL')


class StringMessage(messages.Message):
    message = messages.StringField(1, required=True)