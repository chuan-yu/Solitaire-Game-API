# Solitaire Game API
## Introduction
This is a Solitaire Game API with endpoints with which a front-end can be developed for the game.

## Game Description
Solitaire is played with a standard 52-card deck, without Jokers. After shuffling, seven piles of cards are laid from left to right. Each pile begins with one upturned card. From left to right, each pile contains one more card than the last. The first and left-most pile contains a single upturned card, the second pile contains two cards (one downturned, one upturned), the third contains three (two downturned, one upturned), and so on, until the seventh pile which contains seven cards (six downturned, one upturned).

The four foundations are built up by suit from Ace to King, and the tableau piles can be built down by alternate colors, and partial or complete piles can be moved if they are built down by alternate colors also. Any empty piles can be filled with a King or a pile of cards with a King. The aim of the game is to build up a stack of cards starting with two and ending with King, all of the same suit. Once this is accomplished, the goal is to move this to a foundation, where the player has previously placed the Ace of that suit. Once the player has done this, they will have "finished" that suit, the goal being to finish all suits, at which time the player would have won. 

## Files Included
- api.py: Contains endpoints
- app.yaml: App configuration
- cron.yaml: Cron job configuration
- models.py: Entity and message definitions including helper functions
- solitaire.py: Contains game playing logic
- utils.py: Helper function for retrieving ndb.Models by ulrsafe Key string
- jsonpickle: Library used to convert Python objects to JSON objects
- termcolor.py: Module used to print colorful output in the Python console

## Testing
### Game Playing Logic Test
The game playing logic is contained in solitaire.py file. To test it, un-comment the test code at the end of the file and use Python to launch it.

A move can be made by entering commands in the Python console. Examples of moves that can be made:

- Deal a card: enter ```DEAL```
- Show the top card of pile 1: enter ```SHOW,PILE_1```
- Move a card from deck to pile 1: enter ```MOVE,DECK,PILE_1,-1```
- Move 3 cards from pile 1 to pile 2: enter ```MOVE,PILE_1,PILE_2,-3```
- Move a card from pile 1 to foundation 2: enter ```MOVE,PILE_1,FOUNDATION_2,-1```

**Cards in each stack are printed in color in the console after each move.**

### API Test ###
**It is recommended to test the API on a local machine because card stacks can be seen on the GAE logs window**

#### Test Locally
- Download the project files from: ```https://github.com/yuchuan8/Solitaire-Game-API```
- Run the project using Google App Engine
- If Chrome is used, launch Chrome using command ```[path-to-Chrome] --user-data-dir=test --allow-running-insecure-content```. For example: ```/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --user-data-dir=test --allow-running-insecure-content```
- Visit ```localhost:8080/_ah/api/explorer```. Port number may be different depending on your local setup.
- When creating a new game or making a move, the cards in each stack will be printed on the log window. This is to make test results easier to understand.

#### Test Online
- Visit ```solitaire-game.appspot.com/_ah/api/explorer```

## Endpoints Included:
- **create_user**
	- Path: 'user'
	- Method: POST
	- parameters: user_name, email (optional)
	- Returns: Message confirming creation of the User.
	- Description: Create a new User. user_name provided must be unique. Will raise a ```ConflictException``` if a User with that usernmae already exists
- **new_game**
	- Path: 'game'
	- Method: POST
	- Parameters: user_name
	- Returns: GameForm with initial game state
	- Description: Create a new Game. user_name provided must correspon to an existing user - will raise a ```NotFoundException``` if not.
- **get_game**
	- Path: 'game/{urlsafe_game_key}'
	- Method: GET
	- Parameters: urlsafe_game_key
	- Returns: GameForm with current game state
	- Description: Returns the current state of a game
- **cancel_game**
	- Path: '/game/cancel_game/{urlsafe_game_key}
	- Method: POST
	- Parameters: urlsafe_game_key
	- Returns: Message confirming the game is deleted
	- Description: Delete an incomplete game together with its history from the database
- **make_move**
	- Path: 'game/{urlsafe_game_key}'
	- Method: POST
	- Parameters: urlsafe_game_key, action, origin, destination, card_position
	- Returns: GameForm with the new game state
	- Description: Used to show cards and move cards around. 
		- action allowed: `DEAL`, `MOVE`, `SHOW`
		- origin: For `SHOW` action, this is the pile for which the top card to be show. For `MOVE`, this is the source pile. Not required for `DEAL`. Values allowed: `DECK`, `PILE_[0-6]`, `FOUNDATION_[0-3]`
		- destination: For `MOVE`, it is the desination of the cards to be moved. Not required for `DEAL` and `SHOW`. Values allowed: `PILE_[0-6]`, `FOUNDATION_[0-3]`
		- card_position: The begining position of the card to be moved. Default value is -1. Alwasy negative meaning position from the end of the stack. Not required for `DEAL` and `SHOW`
- **get_scores**
	- Path: 'scores'
	- Method: GET
	- Parameters: None
	- Return: ScoreForms
	- Description: Return all scores in the database (unscored)
- **get_user_scores**
 	- Path: 'score/user/{user_name}'
	- Method: GET
	- Parameters: user_name
	- Return: ScoreForms
	- Description: Return all scores by a User (unordered). Will raise a `NotFoundException` if the User does not exist.
-  **get_best_scores**
	- Path: 'score/best_scores{number_of_results}'
	- Method: GET
	- Parameters: number_of_results
	- Return: ScoreForms
	- Description: Return the best scores limited by number_of_results
- **get_user_ranking**
	- Path: 'rankings/{number_of_results}'
	- Method: GET
	- Parameters: number_of_results
	- Return: UserBestResultsForms
	- Description: Return users' rankings based on their least number of moves
- **get_game_history**
	- Path: 'history/{urlsafe_game_key}'
	- Method: GET
	- Parameters: urlsafe_game_key
	- Return: GameHistoryForms
	- Description: Return the history of a game

## Models Included:
- **User**
	- Store unique user_name and (optional) email address

- **Game**
	- Store unique game states. Its ancestor is User

- **Score**
	- Records completed games. Associate with User model via KeyProperty

- **GameHistory**
	- Records every moves of a game. Its ancestor is Game

## Forms Included:
- **CardForm**
	- Representation of a playing card (suit, number, color, upturned

- **CardForms**
	- Multiple CardForm container

- **GameForm**
	- Representation of a game' state (urlsafe_key, moves, game_over, piles, foundations, deck, open_deck, message)

- **GameForms**
	- Multiple GameForm container

- **NewGameForm**
	- Used to create a new game (user_name)

- **MakeMoveForm**
	- Inbound make move form (action, origin, destination, card_position)

- **ScoreForm**
	- Representation of a completed game's score (user_name, date, moves)

- **ScoreForms**
	- Multiple ScoreForm container

- **UserBestResultForm**
	- Outbound User best result information (user, least_moves)

- **UserBestResultForms**
	- Multiple UserBestResultForm containers

- **GameHistoryForm**
	- Representation of a game's history (sequence, piles, foundations, deck, open_deck)

- **GameHistoryForms**
	- Multiple GameHistoryForm container

- **StringMessage**
	- General purpose String containers (message)	

