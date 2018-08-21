class DiscardBoard():

    def __init__(self):

        self.hearts_discarded = []
        self.diamonds_discarded = []
        self.clubs_discarded = []
        self.spades_discarded = []


    def add_to_board(self, discarded_card):

        suit = int(discarded_card / 13)

        if (suit == 0):
            self.clubs_discarded.append(discarded_card)
        elif (suit == 1):
            self.diamonds_discarded.append(discarded_card)
        elif (suit == 2):
            self.hearts_discarded.append(discarded_card)
        elif (suit == 3):
            self.spades_discarded.append(discarded_card)


    def remove_from_board(self, discarded_card):

        suit = int(discarded_card / 13)

        success = False

        if (suit == 0):

            if (discarded_card in self.clubs_discarded):
                self.clubs_discarded.remove(discarded_card)
                success = True

        elif (suit == 1):

            if (discarded_card in self.diamonds_discarded):
                self.diamonds_discarded.remove(discarded_card)
                success = True

        if (suit == 2):

             if (discarded_card in self.hearts_discarded):
                self.hearts_discarded.remove(discarded_card)
                success = True

        elif (suit == 3):

            if (discarded_card in self.spades_discarded):
                self.spades_discarded.remove(discarded_card)
                success = True

        return success


    def discarded_cards_exist(self):

        discarded_cards = len(self.hearts_discarded) + len(self.diamonds_discarded) + len(self.clubs_discarded) + len(self.spades_discarded)

        return (discarded_cards > 0)

