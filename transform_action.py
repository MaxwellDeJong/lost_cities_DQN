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
