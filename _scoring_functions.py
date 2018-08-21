def ace_degenerate_scoring(suit, played_suit):
    '''Determines if an alternative score must be calculate treating the ace as '1'.'''

    multipliers = [0, 10, 11, 12]

    # Aces are the 1st card of each suit
    ace = 13 * range(4)[suit]

    # Check if an ace has been played
    if (ace in played_suit):

        ace_idx = played_suit.index(ace)

        # Check if ace is the last card
        if (ace_idx == len(played_suit) - 1):
            return True

        next_card = played_suit[ace_idx + 1]

        # Make sure that the card following the ace is a number card
        if (next_card not in multipliers):

            return True

    return False


def get_face_vals(played_suit):

    face_vals = [None] * len(played_suit)

    for i in range(len(face_vals)):
        face_vals[i] = played_suit[i] % 13

    return face_vals


def calc_score_ace_val(played_suit):
    '''Calculates the final score treating the ace as '1'.'''

    num_mult= num_multipliers(played_suit) - 1
    card_sum = sum_cards(played_suit) + 1

    return (num_mult + 1) * (card_sum - 20)


def num_multipliers(played_suit):

    face_vals = get_face_vals(played_suit)

    num_mult = 0
    multipliers = [0, 10, 11, 12]

    for i in range(len(face_vals)):

        card = face_vals[i]

        if card in multipliers:
            num_mult += 1

        else:
            return num_mult

    return num_mult


def sum_cards(played_suit):
    '''Calculate the sum of number cards.'''

    tot_sum = 0
    multipliers = [0, 10, 11, 12]

    face_vals = get_face_vals(played_suit)

    # Initialize assuming that only multipliers are laid
    initial_idx = len(played_suit)

    for i in range(len(played_suit)):

        card = face_vals[i]

        if (card not in multipliers):

            initial_idx = i
            break

    for i in range(initial_idx, len(played_suit)):

        face_val = face_vals[i]

        tot_sum += (face_val + 1)

    return tot_sum
