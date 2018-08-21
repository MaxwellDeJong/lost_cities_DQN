## Each ``turn'' consists of 3 different actions that must be specified:
##   (1) Which card is to be acted upon
##   (2) Whether the card is to be played or discarded
##   (3) Which card is to be drawn
#
## We have 8 cards, so this contribution to the final action will be an integer between 0-7 to 
## specify which card is to be used
##
## We will use 0 to denote playing a card, and 1 to denote discarding the current card
##
## There are potentially 5 different stacks upon which to draw a card. We will use 0 for drawing
## from the deck, 1 for drawing from the discarded Clubs, 2 for drawing from Diamonds, 3 for
## drawing from Hearts, and 4 for drawing from discarded Spades
##
## This leaves us with a total of 8 * 2 * 5 = 80 possible actions. However, in general only a subset
## of these will be permissible based upon the discarded cards as well as the valid plays
##
## As an example, the integer 410 corresponds to discarding the 4th card in our hand and then drawing
## from the deck
#
#def generate_action_dict():
#    '''Generate a dictionary that maps between the 3 different actions needed to completely
#    specify a turn to an integer that summarizes all of these actions.'''
#
#    cards_enum= range(8)
#    card_action_enum = range(2)
#    draw_enum = range(5)
#
#    state_list = []
#
#    for card in cards_enum:
#        for card_action in card_action_enum:
#            for draw in draw_enum:
#
#                state = str(card) + str(card_action) + str(draw)
#                state_list.append(state)
#
#    state_dict = dict(enumerate(state_list))
#
#    return state_dict


def unpack_action(action):

    cards_in_deck = 52

    draw_int = int(action / (2 * cards_in_deck))

    remainder = action % (2 * cards_in_deck)

    play = int(remainder / cards_in_deck)
    card_int = remainder % cards_in_deck

    return (card_int, play, draw_int)


def pack_action(card_int, play, draw_int):

    cards_in_deck = 52

    if play:
        row_val = card_int + cards_in_deck
    else:
        row_val = card_int

    offset = (2 * cards_in_deck * draw_int)

    return row_val + offset

    return row_val * (draw_int + 1)

