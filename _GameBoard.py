from _PlayerBoard import PlayerBoard
from _DiscardBoard import DiscardBoard
from _Deck import Deck
from _GamePlay import make_move

class GameBoard():

    def __init__(self):

        # Set variables for the game
        self.cards_remaining = 52 - 16

        # Create a deck and shuffle it 3 times
        self.deck = Deck()

        self.p1_board = PlayerBoard(self.deck.deal_hand())
        self.p2_board = PlayerBoard(self.deck.deal_hand())

        self.discard_board = DiscardBoard()


    def report_score(self, player):

        if (player == 1):
            player_board = self.p1_board
        else:
            player_board = self.p2_board

        return player_board.tally_score()
