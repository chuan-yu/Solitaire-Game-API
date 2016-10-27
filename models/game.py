from google.appengine.ext import ndb
from game_forms import GameForm
from models_utils import card_deck_objects_to_message_field
from models_utils import byteify
import json

class Game(ndb.Model):
    """Game object"""
    moves = ndb.IntegerProperty(required=True)
    game_over = ndb.BooleanProperty(required=True)
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