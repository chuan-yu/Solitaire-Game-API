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


class Card:
    def __init__(self, suit, number, color, upturned):
        self.suit = suit
        self.number = number
        self.color = COLOR[suit]
        self.upturned = upturned

    def show(self):
        self.upturned = True

    def print_card(self):

        if self is None:
            print u"\u2B1C"
            return

        if self.suit == 'club':
            suit = u"\u2663"
        elif self.suit == 'diamond':
            suit = u"\u2666"
        elif self.suit == 'heart':
            suit = u"\u2665"
        else:
            suit = u"\u2660"

        visible = ''
        if self.upturned:
            visible = 'v'
        if self.color == 'red':
            color = 'red'
        else:
            color = 'grey'

        if self.upturned:
            print colored(suit + str(self.number), color),
        else:
            print u"\u25FC",



class Stack:
    def __init__(self):
        self.cards = []


    def addable(self, card):
        pass

    def add(self, card):
        self.cards.append(card)


    def remove(self):
        del self.cards[-1]

    def show_top_card(self):
        self.cards[-1].show()

    def is_empty(self):
        return self.cards == []


class Pile(Stack):
    def addable(self, cards):
        card = cards[0]
        if self.cards == []:
            return card.number == NVALUES

        top_card = self.cards[-1]
        print 'number: ' + str(card.number) + ' ' + str(top_card.number)
        print 'color: ' + card.color + ' ' + top_card.color
        return card.number == top_card.number - 1 and card.color != top_card.color

class Foundation(Stack):
    def addable(self, cards):
        if len(cards) != 1:
            return False

        if self.cards == []:
            return cards[0].number == 1

        top_card = self.cards[-1]
        return cards[0].suit == top_card.suit and cards[0].number == top_card.number + 1

class Deck(Stack):
    def addable(self, cards):
        return False

    def fill(self):
        for s in SUITS:
            for i in range(1, NVALUES + 1):
                card = Card(suit=s,
                            number=i,
                            color= COLOR[s],
                            upturned=False)
                self.add(card)

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

class OpenDeck(Stack):
    def addable(self, cards):
        return True

def pick_random_elements(data, number):
    size = len(data)
    picked = []
    while number:
        number = number - 1
        size = size - 1
        index = randint(0, size)
        elem = data[index]
        data[index] = data[size]
        picked.append(elem)

    return [picked, data[0:size]]


def print_deck(deck):
    for c in deck:
        c.print_card()

class SolitaireGame:

    def __init__(self, piles, foundations, deck, open_deck):
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

        self.game_over = False

    def new_game(self):
        self.deck = Deck()
        self.deck.fill()
        self.deck.shuffle()
        self.open_deck  = OpenDeck()

        for i in range(0, NPILES):
            self.piles.append(Pile())

            for c in self.deck.cards[-1-i:]:
                self.piles[i].add(c)

            self.piles[i].show_top_card()

            for _ in range(i+1):
                self.deck.remove()

        self.foundations = []
        for i in range(NSUITS):
            self.foundations.append(Foundation())


    def deal(self):
        if self.deck.is_empty():
            self.open_deck.cards.reverse()
            self.deck.cards = self.open_deck.cards
            self.open_deck.cards = []

        top_card = self.deck.cards[-1]
        top_card.show()
        self.open_deck.add(top_card)
        self.deck.remove()

    def move(self, origin, destination, card_position=-1):
        # determine source stack
        if origin[0] == 'p':
            source = self.piles[int(origin[1])]

        if origin[0] == 'd':
            source = self.open_deck

        # determine cards to be moved
        if origin[0] == 'p' and destination[0] == 'p':
            cards = source.cards[int(card_position):]
        else:
            cards = [source.cards[-1]]

        if cards[0].upturned == False:
            print "Cannot move downturned cards"
            return

        for c in cards:
            c.print_card()

        # determine target stack
        if destination[0] == 'p':
            target = self.piles[int(destination[1])]

        if destination[0] == 'f':
            target = self.foundations[int(destination[1])]


        # make the move
        if target.addable(cards):
            print "movable"
            for c in cards:
                target.add(c)

            for _ in range(len(cards)):
                source.remove()

    def show_top(self, pile_number):
        self.piles[int(pile_number)].show_top_card()


    def has_won(self):
        won = True
        for f in self.foundations:
            if len(f.cards) != NVALUES:
                won = False
        return won

    def start(self):
        while not self.has_won():
            command = raw_input("Enter your command: ")
            if command[0] == 'd':
                self.deal()
            if command[0] == 'm':
                command = command.split(',')
                source = command[1]
                destination = command[2]
                card_position = command[3]
                self.move(source, destination, card_position)
            if command[0] == 's':
                command = command.split(',')
                pile_number = command[1]
                self.show_top(pile_number)

            self.print_game()

    def print_game(self):
        print 'Open Deck',
        if self.open_deck.cards == []:
            print u"\u25A1",
        else:
            self.open_deck.cards[-1].print_card(),
        print ' '

        print 'Foundations'
        for f in self.foundations:
            if f.cards == []:
                print u"\u25A1",
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

game = SolitaireGame(None, None, None, None)
game.new_game()
test = jsonpickle.encode(game.piles)
print test




