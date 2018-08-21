from transform_action import pack_action

def find_all_valid_actions(player_board, top_discards):

    hand = player_board.hand

    valid_discards = hand

    valid_plays = []

    for card in hand:

        valid_play = player_board.valid_play(card)

        if (valid_play):
            valid_plays.append(card)

    valid_draws = [0,]

    for suit_int in range(1, 5):

        if (top_discards[suit_int-1] != -1):
            valid_draws.append(suit_int)

    valid_actions = []

    for discard in valid_discards:
        for draw in valid_draws:

            valid_actions.append(pack_action(discard, 0, draw))

            if (discard in valid_plays):

                valid_actions.append(pack_action(discard, 1, draw))

    return valid_actions

