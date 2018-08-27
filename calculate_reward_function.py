from _scoring_functions import ace_degenerate_scoring, calc_score_ace_val, num_multipliers
import numpy as np


def get_face_vals(played_suit):

    face_vals = [None] * len(played_suit)

    for i in range(len(face_vals)):
        face_vals[i] = played_suit[i] % 13

    return face_vals


def weight_sum_cards(played_suit, hand):
    '''Calculate the sum of number cards.'''

    hand_weight = 1
    possible_weight = 0.5

    tot_sum = 0

    for i in range(0, len(played_suit)):

        card = played_suit[i]

        if card in hand:
            weight = hand_weight
        else:
            weight = possible_weight

        face_val = card + 1

        tot_sum += face_val * weight

    return tot_sum


def get_state_information(gameboard, player):

    if (player == 1):
        player_board = gameboard.p1_board
        opp_player_board = gameboard.p2_board
    else:
        player_board = gameboard.p2_board
        opp_player_board = gameboard.p1_board

    num_mult = np.zeros(4, dtype=np.int8)

    clubs = get_face_vals(player_board.played_clubs)
    diamonds = get_face_vals(player_board.played_diamonds)
    hearts = get_face_vals(player_board.played_hearts)
    spades = get_face_vals(player_board.played_spades)

    played_suits = [clubs, diamonds, hearts, spades]
    print 'played suits: ', played_suits

    for suit in num_mult:

        played_suit = played_suits[suit]

        num_mult[suit] = num_multipliers(played_suit)

    excluded_clubs = clubs + get_face_vals(opp_player_board.played_clubs)
    excluded_diamonds = diamonds + get_face_vals(opp_player_board.played_diamonds)
    excluded_hearts = hearts + get_face_vals(opp_player_board.played_hearts)
    excluded_spades = spades + get_face_vals(opp_player_board.played_spades)

    excluded_suits = [excluded_clubs, excluded_diamonds, excluded_hearts, excluded_spades]

    all_mults = [0, 10, 11, 12]

    for suit in range(4):

        excluded_suit = excluded_suits[suit]

        for mult in all_mults:
            
            if (mult in excluded_suit):

                excluded_suit.remove(mult)

    hand_clubs = []
    hand_diamonds = []
    hand_hearts = []
    hand_spades = []

    hand_cards = [hand_clubs, hand_diamonds, hand_hearts, hand_spades]

    hand = player_board.hand
    for hand_card in hand:

        suit = int(hand_card / 13)

        face_val = get_face_vals([hand_card,],)[0]
        hand_cards[suit].append(face_val)

    return (num_mult, hand_cards, played_suits, excluded_suits)



def calc_possible_additional_mults(suit, excluded_suit):

    all_mults = [0, 10, 11, 12] * (suit + 1)

    n_possible_additional_mult = 0

    for mult in all_mults:

        if (mult not in excluded_suit):

            n_possible_additional_mult += 1

    return n_possible_additional_mult


def calc_suit_score(suit, played_suit, num_mult, hand_suit):

    suit_sum = weight_sum_cards(played_suit, hand_suit)

    score = (num_mult + 1) * (suit_sum - 20)

    if (ace_degenerate_scoring(suit, played_suit)):

        score = max(score, calc_score_ace_val(played_suit))

    return score


def calc_max_score(suit, played_suit, excluded_suit, hand, num_mult, n_cards):
    '''Let's assume that the number of multipliers is fixed and calculate the maximum
    score with the current number of multipliers.'''

    if (n_cards == 0):
        return 0

    number_cards = range(1, 10)
    max_cards_remaining = len(number_cards) - len(excluded_suit)

    theoretical_played_suit = played_suit[:]

    all_mults = [0, 10, 11, 12]

    if (played_suit != []):
        lowest_played_card = np.min(played_suit)
    else:
        lowest_played_card = None

    if (n_cards > max_cards_remaining):

        for card in played_suit:

            if (lowest_played_card != None):

                theoretical_played_suit.append(card)

            elif (card > lowest_played_card):

                theoretical_played_suit.append(card)

        return calc_suit_score(suit, theoretical_played_suit, num_mult, hand)

    valid_cards = list(set(number_cards) - set(excluded_suit))
    n_valid_cards = len(valid_cards)
    n_cards_to_add = n_valid_cards - n_cards

    cards_to_add = valid_cards[n_cards_to_add:]

    for card in cards_to_add:

        theoretical_played_suit.append(card)

    return calc_suit_score(suit, theoretical_played_suit, num_mult, hand)


def calc_max_reward(gameboard, player):

    n_cards_remaining = gameboard.cards_remaining
    n_cards_to_play = int(np.ceil(n_cards_remaining / 2))

    (num_mult, hand, played_suits, excluded_suits) = get_state_information(gameboard, player)

    max_score = -1000

    for i in range(n_cards_to_play):
        for j in range(i, n_cards_to_play):
            for k in range(i + j, n_cards_to_play):
                for l in range(i + j + k, n_cards_to_play):

                    clubs_score = calc_max_score(0, played_suits[0], excluded_suits[0], hand[0], num_mult[0], i)
                    diamonds_score = calc_max_score(1, played_suits[1], excluded_suits[1], hand[1], num_mult[1], j)
                    hearts_score = calc_max_score(2, played_suits[2], excluded_suits[2], hand[2], num_mult[2], k)
                    spades_score = calc_max_score(3, played_suits[3], excluded_suits[3], hand[3], num_mult[3], l)

                    tot_score = (clubs_score + diamonds_score + hearts_score + diamonds_score)

                    max_score = max(max_score, tot_score)

    return max_score
