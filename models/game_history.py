from google.appengine.ext import ndb
from game_history_forms import GameHistoryForm
from models_utils import card_deck_objects_to_message_field, byteify
import json

class GameHistory(ndb.Model):
    """GameHistory object"""
    sequence = ndb.IntegerProperty(required=True)
    piles = ndb.JsonProperty(required=True)
    foundations = ndb.JsonProperty(required=True)
    deck = ndb.JsonProperty(required=True)
    open_deck = ndb.JsonProperty(required=True)

    @classmethod
    def new_history(cls, game, sequence, piles, foundations, deck, open_deck):
        history = GameHistory(parent=game, sequence=sequence,
                              piles=piles, foundations=foundations,
                              deck=deck, open_deck=open_deck)
        history.put()

    def to_form(self):
        form = GameHistoryForm()
        form.sequence = self.sequence
        form.piles = card_deck_objects_to_message_field(byteify(json.loads(self.piles)))
        form.foundations = card_deck_objects_to_message_field(byteify(json.loads(self.foundations)))
        form.deck = card_deck_objects_to_message_field(byteify(json.loads(self.deck)))
        form.open_deck = card_deck_objects_to_message_field(byteify(json.loads(self.open_deck)))
        return form