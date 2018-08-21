from _scoring_functions import *

class PlayerBoard():

    def __init__(self, initial_hand):

        self.hand = initial_hand[:]
        
        self.played_hearts = []
        self.played_diamonds = []
        self.played_clubs = []
        self.played_spades = []


    def query_played_cards(self, suit):
        '''Return the cards played for a specified suit.'''

        if (suit == 0):
            return self.played_clubs
        elif (suit == 1):
            return self.played_diamonds
        elif (suit == 2):
            return self.played_hearts
        elif (suit == 3):
            return self.played_spades

        else:
            print 'Invalid suit provided.'
            print 'Suit given: ', suit


    def remove_card(self, card):

        self.hand.remove(card)


    def add_card(self, card):

        self.hand.append(card)


    def play_card(self, card):
        '''Pass in an integer between 0 and 3 for the suit and an integer between
        0 and 12 for the card.'''

        suit = int(card / 13)

        if (suit == 0):
            self.played_clubs.append(card)
        elif (suit == 1):
            self.played_diamonds.append(card)
        elif (suit == 2):
            self.played_hearts.append(card)
        elif (suit == 3):
            self.played_spades.append(card)

        self.hand.remove(card)


    def suit_initialized(self, suit):
        '''Check if a numerical card has been played for a given suit.'''

        played_suit = self.query_played_cards(suit)

        #number_cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10']
        number_cards = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        if (played_suit == []):
            return False

        # check if any of the number cards have been played
        for number in number_cards:
            if (number in played_suit):
                return True

        return False


    def valid_play(self, card):
        '''Check if a proposed move is valid.'''

        suit = int(card / 13)
        face = card % 13

        #multipliers = ['a', 'j', 'q', 'k']
        #number_cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10']

        multipliers = [0, 10, 11, 12]
        number_cards = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        played_suit = self.query_played_cards(suit)

        isInitialized = self.suit_initialized(suit)

        # If no number cards have been played, any card is valid
        if not isInitialized:
            return True

        if face in multipliers:
            return False

        lowest_card_played = self.find_lowest_card(suit)

        if (lowest_card_played in multipliers):
            return True

        if (face > lowest_card_played):
            return True

        return False


    def card_exists(self, card):

        return (card in self.hand)


    def find_lowest_card(self, suit):
        '''Return the smallest possible valid card to be added.'''

        played_suit = self.query_played_cards(suit)

        # The played cards are in order, and the suit is already initialized and the list 
        # is not empty.
        lowest_card = played_suit[-1]

        return lowest_card


    def tally_score(self):

        clubs = self.played_clubs
        diamonds = self.played_diamonds
        hearts = self.played_hearts
        spades = self.played_spades

        tot_score = 0

        played_cards = [clubs, diamonds, hearts, spades]

        for suit in range(4):

            played_suit = played_cards[suit]

            if (played_suit != []):

                num_mult = num_multipliers(played_suit)
                suit_sum = sum_cards(played_suit)

                score = (num_mult + 1) * (suit_sum - 20)

                if (ace_degenerate_scoring(suit, played_suit)):

                    score = max(score, calc_score_ace_val(played_suit))

                tot_score += score 

        return tot_score
