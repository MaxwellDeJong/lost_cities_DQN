import sys
import numpy as np

class Deck:
    """A class of a deck of playingcards"""
    def __init__(self):

        deckofcards = np.arange(52)
        np.random.shuffle(deckofcards)

        deck_list = deckofcards.tolist()

        self.deckofcards = deck_list


    def draw_card(self):

        return self.deckofcards.pop(0)


    def deal_hand(self):

        hand_size = 8
        hand = []

        for i in range(hand_size):
            hand.append(self.deckofcards.pop(0))

        return hand
