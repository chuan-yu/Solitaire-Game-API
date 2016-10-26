from random import randint
from termcolor import colored, cprint

import jsonpickle

SUITS = ['club', 'diamond', 'heart', 'spade']
COLOR = {}
for s in ['club', 'spade']:
    COLOR[s] = 'black'
for s in ['diamond', 'heart']:
    COLOR[s] = 'red'


NPILES = 7
NSUITS = 4
NVALUES = 13

# Class to model a playing card
class Card:
    def __init__(self, suit, number, color, upturned):
        self.suit = suit
        self.number = number
        self.color = COLOR[suit]
        self.upturned = upturned

    def show(self):
        self.upturned = True

    # print the card in command window
    def print_card(self):
        # there is no card, print a blank square
        if self is None:
            print u"\u2B1C".encode('utf-8')
            return

        # print shapes insteads of suit names
        if self.suit == 'club':
            suit = u"\u2663".encode('utf-8')
        elif self.suit == 'diamond':
            suit = u"\u2666".encode('utf-8')
        elif self.suit == 'heart':
            suit = u"\u2665".encode('utf-8')
        else:
            suit = u"\u2660".encode('utf-8')

        # Change the text color according to the card color
        if self.color == 'red':
            color = 'red'
        else:
            color = 'grey'

        # If the card is downturned, print a solid black square
        if self.upturned:
            print colored(suit + str(self.number), color),
        else:
            print u"\u25FC".encode('utf-8'),

# A general card stack class which other specific card
# classes will inherit
class Stack:
    def __init__(self):
        self.cards = []

    # Determine whether new cards can be added to the
    # end of the stack
    def addable(self, card):
        pass

    # Add a new card to the end of the stack
    def add(self, cards):
        if type(cards) is not list:
            self.cards.append(cards)
        else:
            self.cards.extend(cards)

    # Remove the top card from the stack
    def remove(self):
        del self.cards[-1]

    #   Show the top card
    def show_top_card(self):
        self.cards[-1].show()

    # Determine whether the stack is empty
    def is_empty(self):
        return self.cards == []

# The class to model the pile
class Pile(Stack):
    def addable(self, cards):
        card = cards[0]

        # If the pile is empty, only a stack starting
        # with King can be added to the pile
        if self.is_empty():
            return card.number == NVALUES

        # A pile is addable only when the first card of the stack
        # to be added has a value 1 less than the value of the pile
        # top card and the color of the two cards are different
        top_card = self.cards[-1]
        return card.number == top_card.number - 1 and card.color != top_card.color

    # Check if the top card of the pile is upturned
    def top_card_upturned(self):

        return self.cards[-1].upturned

# The class to model the foundation
class Foundation(Stack):
    def addable(self, cards):

        # Only one card can be added to the foundation
        # at a time
        if len(cards) != 1:
            return False

        # If the foundation is empty, only Ace can be added
        if self.is_empty():
            return cards[0].number == 1

        # The card to be added has to be of the same suit
        # and the value has to be 1 larger than that of the top card
        top_card = self.cards[-1]
        return cards[0].suit == top_card.suit and cards[0].number == top_card.number + 1

# The class to model the deck
class Deck(Stack):

    # No cards should be allowed to add the deck
    def addable(self, cards):
        return False

    # Fill the deck with cards
    def fill(self):
        for s in SUITS:
            for i in range(1, NVALUES + 1):
                card = Card(suit=s,
                            number=i,
                            color= COLOR[s],
                            upturned=False)
                self.add(card)

    def downturn_all(self):
        for c in self.cards:
            c.upturned = False

    # Shuffle the deck
    def shuffle(self):
        new_cards = []
        size = len(self.cards)
        while size:
            size = size - 1
            index = randint(0, size)
            elem = self.cards[index]
            self.cards[index] = self.cards[size]
            new_cards.append(elem)
        self.cards = new_cards

# A class to model the open deck. After a card is dealed,
# it is moved to the open deck. The open deck cards are upturned
class OpenDeck(Stack):
    def addable(self, cards):
        return True

# A class to model the game
class SolitaireGame:

    def __init__(self, piles, foundations, deck, open_deck, game_over):
        if piles is None:
            self.piles = []
        else:
            self.piles = piles

        if foundations is None:
            self.foundations = []
        else:
            self.foundations = foundations

        if deck is None:
            self.deck = []
        else:
            self.deck = deck

        if open_deck is None:
            self.open_deck = []
        else:
            self.open_deck = open_deck

        self.game_over = game_over

    # Start a new game
    def new_game(self):
        self.deck = Deck()
        # Fill the deck with cards
        self.deck.fill()
        # Shuffle the deck
        self.deck.shuffle()

        # Create an empty open deck
        self.open_deck  = OpenDeck()

        # Fill the piles. The first pile gets 1 card,
        # the second gets 2 cards, the third 3 cards,
        # so on and so forth
        for i in range(0, NPILES):
            self.piles.append(Pile())

            self.piles[i].add(self.deck.cards[-1-i:])

            self.piles[i].show_top_card()

            for _ in range(i+1):
                self.deck.remove()

        # Create NSUITS empty foundations
        self.foundations = []
        for i in range(NSUITS):
            self.foundations.append(Foundation())

        self.print_game()

    # Deal a card
    def deal(self):
        # If there are no cards left in the deck,
        # move all cards from open deck back to the deck
        if self.deck.is_empty():
            self.open_deck.cards.reverse()
            self.deck.cards = self.open_deck.cards
            self.deck.downturn_all()
            self.open_deck.cards = []

        # Show the top card of the deck and move it to the open deck
        top_card = self.deck.cards[-1]
        top_card.show()
        self.open_deck.add(top_card)
        self.deck.remove()

    # Make a move. Return True if a move is made
    def move(self, origin, destination, card_position=-1):
        if '_' in origin:
            origin_splitted = origin.split('_')
            origin_name = origin_splitted[0]
            origin_no = int(origin_splitted[1])
        else:
            origin_name = origin

        if '_' in destination:
            destination_splitted = destination.split('_')
            destination_name = destination_splitted[0]
            destination_no = int(destination_splitted[1])
        else:
            destination_name = destination

        source = None
        target = None
        moved = False

        # determine source stack
        if origin_name == 'PILE':
            source = self.piles[origin_no]

        if origin_name == 'DECK':
            source = self.open_deck

        # determine cards to be moved
        if abs(int(card_position)) > len(source.cards):
            raise Exception("Card Position is out of range")

        if origin_name == 'PILE' and \
           destination_name == 'PILE':
            cards = source.cards[int(card_position):]
        else:
            cards = [source.cards[-1]]

        # If the top card of the cards to be moved are downturned,
        # abort
        if cards[0].upturned == False:
            print "Cannot move downturned cards"
            return

        # determine target stack
        if destination_name == 'PILE':
            target = self.piles[destination_no]


        if destination_name == 'FOUNDATION':
            target = self.foundations[destination_no]

        # make the move
        if target.addable(cards):
            target.add(cards)

            for _ in range(len(cards)):
                source.remove()

            moved = True

        # Check if the game is over after the move
        self.game_over = self.check_win()

        return moved

    # Show the top card of a pile. Return True if showed
    def show_top(self, pile):
        showed = False
        if '_' in pile:
            pile_splitted = pile.split('_')
            pile_name = pile_splitted[0]
            pile_no = int(pile_splitted[1])

        if pile_name != 'PILE':
            raise ValueError("Can only show pile's top card")

        if not self.piles[pile_no].top_card_upturned():
            self.piles[pile_no].show_top_card()
            showed = True

        return showed

    # check whether the user has won the game
    def check_win(self):
        won = True
        for f in self.foundations:
            if len(f.cards) != NVALUES:
                won = False
        return won

    # Start the game. Get inputs from user
    def start(self):
        while not self.check_win():
            command = raw_input("Enter your command: ")
            if command[0] == 'D':
                self.deal()
            if command[0] == 'M':
                command = command.split(',')
                source = command[1]
                destination = command[2]
                card_position = command[3]
                self.move(source, destination, card_position)
            if command[0] == 'S':
                command = command.split(',')
                pile_number = command[1]
                self.show_top(pile_number)

            self.print_game()

    # Print all stacks on the command window
    def print_game(self):
        print 'Open Deck',
        if self.open_deck.cards == []:
            print u"\u25A1".encode('utf-8'),
        else:
            self.open_deck.cards[-1].print_card(),
        print ' '

        print 'Foundations'
        for f in self.foundations:
            if f.cards == []:
                print u"\u25A1".encode('utf-8'),
            else:
                f.cards[-1].print_card()
        print ' '

        print 'Piles'
        i = 0
        for p in self.piles:
            print i,
            i = i + 1
            for c in p.cards:
                c.print_card(),
            print ' '

## Code to test this module ##
## ------------------------ ##
# game = SolitaireGame(None, None, None, None, False)
# game.new_game()
# game.start()

