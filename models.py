from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
import json
# from model_utils import card_deck_objects_to_message_field

class User(ndb.Model):
    """User profile"""
    user_name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()

def card_deck_objects_to_message_field(objects):

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
    """Game object"""
    moves = ndb.IntegerProperty(required=True)
    game_over = ndb.BooleanProperty(required=True)
    # user = ndb.KeyProperty(required=True, kind='User')
    piles = ndb.JsonProperty()
    foundations = ndb.JsonProperty()
    deck = ndb.JsonProperty()
    open_deck = ndb.JsonProperty()

    @classmethod
    def new_game(cls, user, piles, foundations, deck, open_deck):
        """Create and return a new game"""
        game = Game(parent=user,
                    moves=0,
                    game_over=False,
                    piles=piles,
                    foundations=foundations,
                    deck=deck,
                    open_deck=open_deck)
        game.put()
        return game

    def save_game(self):
        """Save the result of the game"""
        score = Score(user=self.user, date=date.today(),
                      moves=self.moves)
        score.put()


    def to_form(self, message):
        """Return a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.moves = self.moves
        form.game_over = self.game_over
        form.piles = card_deck_objects_to_message_field(byteify(json.loads(self.piles)))
        form.foundations = card_deck_objects_to_message_field(byteify(json.loads(self.foundations)))
        form.deck = card_deck_objects_to_message_field(byteify(json.loads(self.deck)))
        form.open_deck = card_deck_objects_to_message_field(byteify(json.loads(self.open_deck)))
        form.message = message
        return form

class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    moves = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().user_name,
                         date=str(self.date), moves=self.moves)

class GameHistory(ndb.Model):
    """GameHistory object"""
    game = ndb.KeyProperty(required=True, kind='Game')
    sequence = ndb.IntegerProperty(required=True)
    piles = ndb.JsonProperty(required=True)
    foundations = ndb.JsonProperty(required=True)
    deck = ndb.JsonProperty(required=True)
    open_deck = ndb.JsonProperty(required=True)

    def to_form(self):
        form = GameHistoryForm()
        form.game = self.game
        form.sequence = self.sequence
        form.piles = card_deck_objects_to_message_field(byteify(json.loads(self.piles)))
        form.foundations = card_deck_objects_to_message_field(byteify(json.loads(self.foundations)))
        form.deck = card_deck_objects_to_message_field(byteify(json.loads(self.deck)))
        form.open_deck = card_deck_objects_to_message_field(byteify(json.loads(self.open_deck)))

class CardForm(messages.Message):
    suit = messages.StringField(1, required=True)
    number = messages.IntegerField(2, required=True)
    color = messages.StringField(3, required=True)
    upturned = messages.BooleanField(4, required=True)

class CardForms(messages.Message):
    cards = messages.MessageField(CardForm, 2, repeated=True)


class GameForm(messages.Message):
    urlsafe_key = messages.StringField(1, required=True)
    moves = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    piles = messages.MessageField(CardForms, 5, repeated=True)
    foundations = messages.MessageField(CardForms, 6, repeated=True)
    deck = messages.MessageField(CardForms, 7, required=True)
    open_deck = messages.MessageField(CardForms, 8, required=True)
    message = messages.StringField(9, required=True)


class GameForms(messages.Message):
    items = messages.MessageField(GameForm, 1, repeated=True)

class NewGameForm(messages.Message):
    user_name = messages.StringField(1, required=True)


class Action(messages.Enum):
    MOVE = 1
    DEAL = 2
    SHOW = 3

class StackName(messages.Enum):
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
    action = messages.EnumField('Action', 1, default='DEAL', required=True)
    origin = messages.EnumField('StackName', 2)
    destination = messages.EnumField('StackName', 3)
    card_position = messages.IntegerField(4)

class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    moves = messages.IntegerField(3, required=True)

class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)

class UserBestResultForm(messages.Message):
    """Form for outbound User best result information"""
    user = messages.StringField(1, required=True)
    least_moves = messages.IntegerField(2, required=True)

class UserBestResultForms(messages.Message):
    """Return multiple UserBestResultForm"""
    items = messages.MessageField(UserBestResultForm, 1, repeated=True)

class GameHistoryForm(messages.Message):
    """Return the form representation of the Game History"""
    game = messages.StringField(1, required=True)
    sequence = messages.IntegerField(2, required=True)
    piles = messages.MessageField(CardForms, 3, repeated=True)
    foundations = messages.MessageField(CardForms, 4, repeated=True)
    deck = messages.MessageField(CardForms, 5, required=True)
    open_deck = messages.MessageField(CardForms, 6, required=True)

class GameHistoryForms(messages.Message):
    """Return multiple GameHistory Form"""
    items = messages.MessageField(GameHistoryForm, 1, repeated=True)

class StringMessage(messages.Message):
    message = messages.StringField(1, required=True)