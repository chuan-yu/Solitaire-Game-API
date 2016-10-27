import logging
import endpoints
from protorpc import remote, messages

from solitaire import SolitaireGame

from models import User
from models import Game
from models import Score
from models import GameHistory
from models import NewGameForm
from models import GameForm
from models import GameForms
from models import MakeMoveForm
from models import ScoreForm
from models import ScoreForms
from models import UserBestResultForm
from models import UserBestResultForms
from models import GameHistoryForm
from models import GameHistoryForms
from models import StringMessage
from models import Action
from models import StackName
from utils import get_by_urlsafe

from google.appengine.ext import ndb
import jsonpickle

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                            email=messages.StringField(2))
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
BEST_SCORE_REQUEST = endpoints.ResourceContainer(
        number_of_results=messages.IntegerField(1))

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
            game_db = Game.new_game(user=user.key,
                                    piles=game_json['piles'],
                                    foundations=game_json['foundations'],
                                    deck=game_json['deck'],
                                    open_deck=game_json['open_deck'])
        except Exception, e:
            logging.error(str(e))

        # Save game history
        game_history = GameHistory.new_history(game=game_db.key,
                                   sequence=game_db.moves,
                                   piles=game_db.piles,
                                   foundations=game_db.foundations,
                                   deck=game_db.deck,
                                   open_deck=game_db.open_deck)

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


    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='game/user/{user_name}',
                      name='get_user_game',
                      http_method='GET')
    def get_user_game(self, request):
        """Return all games created by a user"""
        user = User.query(User.user_name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException("The User does not exist")

        games = Game.query(ancestor=user.key).fetch()
        if not games:
            raise endpoints.NotFoundException("The User does not have any Game")

        return GameForms(items=[game.to_form("Make a move") for game in games])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/cancel_game/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='POST')
    @ndb.transactional
    def cancel_game(self, request):
        """Delete a game from the database"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            # Check that user has the right to delete the game
            current_user = endpoints.get_current_user()
            if current_user.nickname() != game.key.parent().get().user_name:
                raise endpoints.ForbiddenException('You are not authroized ' +
                    'to delete the game')

            if not game.game_over:
                game_history = GameHistory.query(ancestor=game.key).fetch()
                for h in game_history:
                    h.key.delete()
                game.key.delete()
                return StringMessage(message="The game has been deleted!")
            else:
                raise endpoints.ForbiddenException("Not allowed to delete a completed game")
        else:
            raise endpoints.NotFoundException("Game not found")

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
                raise endpoints.BadRequestException('Souce and Destination ' +
                                 'must not be empty for MOVE action')

            if not card_position:
                card_position = -1

        # If action is SHOW, the source field cannot be empty
        if action == Action.SHOW:
            if not origin:
                raise endpoints.BadRequestException('Souce must not be empty for SHOW action')

        # Load the game from DB
        game_db = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game_db:
            raise endpoints.NotFoundException("The Game does not exist")

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

        # To track whether any cards are moved or upturned

        changed = False
        if action == Action.DEAL:
            game.deal()
            changed = True
            game_db.moves += 1
            game.print_game()

        if action == Action.MOVE:
            changed = game.move(origin=str(origin),
                      destination=str(destination),
                      card_position=card_position)
            if changed:
                game_db.moves += 1
            else:
                game.print_game()
                raise endpoints.BadRequestException("Illigal move. Try again.")

            game.print_game()

        if action == Action.SHOW:
            changed = game.show_top(str(origin))

            if changed:
                game_db.moves += 1
            else:
                game.print_game()
                raise endpoints.BadRequestException('Could not show the card.')

            game.print_game()

        # Convert the game to JSON format
        game_json = to_json(game)

        # If changed, update the fields and save in DB
        if changed:
            game_db.piles = game_json['piles']
            game_db.foundations = game_json['foundations']
            game_db.deck = game_json['deck']
            game_db.open_deck = game_json['open_deck']
            game_db.game_over = game_json['game_over']

            game_db.put()

        # If changed, save game history
        if changed:
            game_history = GameHistory.new_history(game=game_db.key,
                                       sequence=game_db.moves,
                                       piles=game_db.piles,
                                       foundations=game_db.foundations,
                                       deck=game_db.deck,
                                       open_deck=game_db.open_deck)

        if game_db.game_over:
            game_db.save_game()

        return game_db.to_form('Made a move')

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        scores = Score.query()
        if not scores:
            raise endpoints.NotFoundException("No Scores found")
        return ScoreForms(items=[score.to_form() for score in scores])

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
        if not scores:
            raise endpoints.NotFoundException("No scores found for this User")

        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=BEST_SCORE_REQUEST,
                      response_message=ScoreForms,
                      path='scores/best_scores/{number_of_results}',
                      name='get_best_scores',
                      http_method='GET')
    def get_best_scores(self, request):
        """Return the best game results"""
        scores = Score.query().order(Score.moves).fetch(int(request.number_of_results))
        if not scores:
            raise endpoints.NotFoundException("No scores found")

        items = [score.to_form() for score in scores]
        return ScoreForms(items=items)

    @endpoints.method(request_message=BEST_SCORE_REQUEST,
                      response_message=UserBestResultForms,
                      path='rankings/{number_of_results}',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return users' rankings based on their least number of moves"""
        rankings = []
        users = User.query().fetch()
        if not users:
            raise endpoints.NotFoundException("No users found")
        # Find the best score for each user, create a form
        # and add it to the rangkings list
        for user in users:
            score_best = Score.query(Score.user == user.key).order(Score.moves).get()
            if not score_best:
                raise endpoints.NotFoundException("No scores available")

            best_result_form = UserBestResultForm(user=score_best.user.get().user_name,
                least_moves=score_best.moves)
            rankings.append(best_result_form)

        # Sort the ranking list based on the least_moves
        rankings.sort(key=lambda x: x.least_moves)
        return UserBestResultForms(items=rankings)

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameHistoryForms,
                      path='history/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return every moves of the game"""
        game_histories = GameHistory.query(ancestor=ndb.Key(urlsafe=request.urlsafe_game_key)).fetch()
        if not game_histories:
            raise endpoints.NotFoundException("No Game Histories found")

        return GameHistoryForms(items=[history.to_form() for history in game_histories])




api = endpoints.api_server([SolitaireAPI])