import logging
import endpoints
from protorpc import remote, messages

from solitaire import SolitaireGame

from models import User
from models import Game
from models import Score
from models import NewGameForm
from models import GameForm
from models import MakeMoveForm
from models import ScoreForm
from models import ScoreForms
from models import StringMessage
from models import Action
from models import StackName
from utils import get_by_urlsafe

import jsonpickle

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                            email=messages.StringField(2))
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)


# Convert Game data to JSON format
def to_json(game):
    piles_json = jsonpickle.encode(game.piles)
    foundations_json = jsonpickle.encode(game.foundations)
    deck_json = jsonpickle.encode(game.deck)
    open_deck_json = jsonpickle.encode(game.open_deck)
    return {'piles': piles_json,
            'foundations': foundations_json,
            'deck': deck_json,
            'open_deck': open_deck_json,
            'game_over': game.game_over}

# Convert JSON object to python SolitaireGame object
def to_python(piles, foundations, deck, open_deck, game_over):
    piles = jsonpickle.decode(piles)
    foundations = jsonpickle.decode(foundations)
    deck = jsonpickle.decode(deck)
    open_deck = jsonpickle.decode(open_deck)

    return SolitaireGame(piles, foundations, deck, open_deck, game_over)

@endpoints.api(name='solitaire', version='1')
class SolitaireAPI(remote.Service):

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a new user"""

        # Check that user already exists
        if User.query(User.user_name == request.user_name).get():
            raise endpoints.ConflictException(
                    "A user with that name already exists")
        # Create a new user
        user = User(user_name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message="User {} created!".format(request.user_name))


    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Create a new game"""
        user = User.query(User.user_name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    "A user with that name does not exist")

        game = SolitaireGame(None, None, None, None, False)
        game.new_game()

        # Convert card stacks to JSON
        game_json = to_json(game)
        try:
            game_db = Game.new_game(user.key,
                                    piles=game_json['piles'],
                                    foundations=game_json['foundations'],
                                    deck=game_json['deck'],
                                    open_deck=game_json['open_deck'])
        except Exception, e:
            logging.error(str(e))

        return game_db.to_form('New game created!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='POST')
    def make_move(self, request):
        """Make a move"""
        action = request.action
        origin = request.origin
        destination = request.destination
        card_position  = request.card_position

        # If action is MOVE, the source and destination
        # field cannot be empty
        if action == Action.MOVE:
            if not origin or not destination:
                raise endpoints.BadRequestError('Souce and Destination ' +
                                 'must not be empty for MOVE action')

            if not card_position:
                card_position = -1

        # If action is SHOW, the source field cannot be empty
        if action == Action.SHOW:
            if not origin:
                raise endpoints.BadRequestError('Souce must not be empty for SHOW action')

        # Load the game from DB
        game_db = get_by_urlsafe(request.urlsafe_game_key, Game)

        # If game is over, copy to form and return
        if game_db.game_over:
            return game_db.to_form('Game already over')

        # Create Python game object
        game = to_python(piles=game_db.piles,
                         foundations=game_db.foundations,
                         deck=game_db.deck,
                         open_deck=game_db.open_deck,
                         game_over=game_db.game_over)

        # Make the move

        if action == Action.DEAL:
            game.deal()
            game_db.moves += 1
            game.print_game()

        if action == Action.MOVE:
            game.move(origin=str(origin),
                      destination=str(destination),
                      card_position=card_position)
            game_db.moves += 1
            game.print_game()

        if action == Action.SHOW:
            game.show_top(str(origin))
            game_db.moves += 1
            game.print_game()

        # Convert the game to JSON format
        game_json = to_json(game)

        # Update the fields and save in DB
        game_db.piles = game_json['piles']
        game_db.foundations = game_json['foundations']
        game_db.deck = game_json['deck']
        game_db.open_deck = game_json['open_deck']
        game_db.game_over = game_json['game_over']

        game_db.put()

        if game_db.game_over:
            game_db.save_game()

        return game_db.to_form('Made a move')

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                          response_message=ScoreForms,
                          path='scores/user/{user_name}',
                          name='get_user_scores',
                          http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.user_name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

api = endpoints.api_server([SolitaireAPI])