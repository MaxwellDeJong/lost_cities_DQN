def get_initial_state():

        p1_hand = [0, 18, 7, 22, 50, 35, 41, 47]
        p2_hand = [3, 10, 49, 30, 5, 11, 29, 21]

        deck = range(52)

        for card in p1_hand:
            deck.remove(card)

        for card in p2_hand:
            deck.remove(card)

        discarded_clubs = [1]
        discarded_diamonds = [16]
        discarded_hearts = [28]
        discarded_spades = [51]

        deck.remove(1)
        deck.remove(16)
        deck.remove(28)
        deck.remove(51)

        discarded_cards = [discarded_clubs, discarded_diamonds, discarded_hearts, discarded_spades]

        p1_played_clubs = [2, 4]
        p1_played_diamonds = []
        p1_played_hearts = [26, 31]
        p1_played_spades = [40]

        p1_played = [p1_played_clubs, p1_played_diamonds, p1_played_hearts, p1_played_spades]

        p2_played_clubs = [6]
        p2_played_diamonds = [13, 14, 15, 17]
        p2_played_hearts = []
        p2_played_spades = [42]

        p2_played = [p2_played_clubs, p2_played_diamonds, p2_played_hearts, p2_played_spades]

        all_played = [p1_played, p2_played]

        for player in range(2):
            for suit in range(4):
                for card in self.all_played[player][suit]:

                    deck.remove(card)

        return (p1_hand, p2_hand, discarded_cards, all_played, deck)



