import logging
import endpoints
from protorpc import remote, messages

from solitaire import SolitaireGame

from models import User, Game
from models import NewGameForm, GameForm, StringMessage

import jsonpickle

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                            email=messages.StringField(2))
# MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
#     MakeMoveForm,
#     urlsafe_game_key=messages.StringField(1),)

@endpoints.api(name='solitaire', version='1')
class SolitaireAPI(remote.Service):

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        if User.query(User.user_name == request.user_name).get():
            raise endpoints.ConflictException(
                    "A user with that name already exists")
        user = User(user_name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message="User {} created!".format(request.user_name))


    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        user = User.query(User.user_name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    "A user with that name does not exist")

        game = SolitaireGame(None, None, None, None)
        game.new_game()
        game.print_game()

        piles_json = jsonpickle.encode(game.piles)
        foundations_json = jsonpickle.encode(game.foundations)
        deck_json = jsonpickle.encode(game.deck)
        open_deck_json = jsonpickle.encode(game.open_deck)

        try:
            game_db = Game.new_game(user.key, piles_json,
                                    foundations_json, deck_json,
                                    open_deck_json)
        except Exception, e:
            logging.error(str(e))

        return game_db.to_form('Good luck!')


api = endpoints.api_server([SolitaireAPI])