from _scoring_functions import ace_degenerate_scoring
 
def draw_new_card(player_board, discard_board, deck, draw, top_discards):

    if (draw == 0):
        new_card = draw_deck_card(player_board, deck)
    else:
        new_card = draw_discarded_card(player_board, discard_board, draw, top_discards)

    return new_card


def draw_deck_card(player_board, deck):

    new_card = deck.draw_card()

    player_board.add_card(new_card)

    return new_card


def draw_discarded_card(player_board, discard_board, draw_int, top_discards):

    # Suits are assigned integers in in alphabetical order: (deck), clubs, diamonds, hearts, spades
    if (draw_int == 1):
        discarded_cards = discard_board.clubs_discarded
    elif (draw_int == 2):
        discarded_cards = discard_board.diamonds_discarded
    elif (draw_int == 3):
        discarded_cards = discard_board.hearts_discarded
    elif (draw_int == 4):
        discarded_cards = discard_board.spades_discarded

    desired_card = discarded_cards[-1]

    if (len(discarded_cards) == 1):
        top_discards[draw_int-1] = -1
    else:
        top_discards[draw_int-1] = discarded_cards[-2]

    successful_draw = discard_board.remove_from_board(desired_card)

    player_board.add_card(desired_card)

    return desired_card


def discard_hand_card(player_board, discard_board, card):

    discard_board.add_to_board(card)
    player_board.remove_card(card)


def update_state_discard(state, discard_card, top_discard, player, p1_obs, p2_obs):

    suit = int(discard_card / 13)
    top_discarded_card = top_discard[suit]

    # Check if player 1 has the current top discarded card and update accordingly
    if state[top_discarded_card] == 7:

        state[top_discarded_card] = 6

        p1_obs[top_discarded_card] = 6
        p2_obs[top_discarded_card] = 6

    else:

        state[top_discarded_card] = 8

        p1_obs[top_discarded_card] = 8
        p2_obs[top_discarded_card] = 8

    # Change the discarded card to the top of its respective suit
    if (player == 1):

        state[discard_card] = 7

        p1_obs[discard_card] = 7
        p2_obs[discard_card] = 7

    elif (player == 2):

        state[discard_card] = 9

        p1_obs[discard_card] = 9
        p2_obs[discard_card] = 9

    # Update the list of top discarded cards
    top_discard[suit] = discard_card


def update_state_draw(state, new_card, player, p1_obs, p2_obs, draw_int):

    if (player == 1):
        state[new_card] = 0
        p1_obs[new_card] = 0

        if (draw_int != 0):
            p2_obs[new_card] = 0

    elif (player == 2):
        state[new_card] = 3
        p2_obs[new_card] = 3

        if (draw_int != 0):
            p1_obs[new_card] = 3


def update_state_play(state, play_card, flex_options, player, player_board, p1_obs, p2_obs):
    '''Update both the state and the flex_options list after a new card is played. At this point
    the hand has been updated but these variables have not, so flex options contains information 
    about flex options before current card played. 'Flex option' elements are:

    -1: suit initialized
    0: no current flex play
    1: flex play for given suit 
    '''

    suit = int(play_card / 13)

    # If the suit was previously initialized, the flex options cannot change
    if (flex_options[suit] == -1):
        return

    played_cards = player_board.query_played_cards(suit)
    flex_option = ace_degenerate_scoring(suit, played_cards)

    # If there was not a previous flex option, we only need to change the state of the new card
    if (flex_options[suit] == 0):

        # If there is a flex option with the addition of the new card, the new card must be the flex
        # option
        if flex_option:

            # Update flex options
            flex_options[suit] = 1

            # Designate card as flex option in state
            if (player == 1):
                state[play_card] = 2
                p1_obs[play_card] = 2
                p2_obs[play_card] = 2
            elif (player == 2):
                state[play_card] = 5
                p1_obs[play_card] = 5
                p2_obs[play_card] = 5

        # If there still isn't a flex option, the new card is simply on the board
        else:

            if (player == 1):
                state[play_card] = 1
                p1_obs[play_card] = 1
                p2_obs[play_card] = 1
            elif (player == 2):
                state[play_card] = 4
                p1_obs[play_card] = 4
                p2_obs[play_card] = 4

    # If there was previously a flex option and a new card is played, we no longer have a flex option
    elif (flex_options[suit] == 1):

        flex_options[suit] == -1

        ace = 13 * suit

        # The previous ace that gave the flex option is now a standard board play.
        # The new card is necessarily a standard board play as well.
        if (player == 1):

            state[ace] = 1
            state[play_card] = 1

            p1_obs[ace] = 1
            p2_obs[ace] = 1
            p1_obs[play_card] = 1
            p2_obs[play_card] = 1

        elif (player == 2):

            state[ace] = 4
            state[play_card] = 4

            p1_obs[ace] = 4
            p2_obs[ace] = 4
            p1_obs[play_card] = 4
            p2_obs[play_card] = 4


def make_move(player_board, discard_board, deck, action, state, top_discard, flex_options, player, p1_obs, p2_obs):

    card = action[0]
    play = action[1]
    draw_int = action[2]

    initial_score = player_board.tally_score()

    if play:
        player_board.play_card(card)
        update_state_play(state, card, flex_options, player, player_board, p1_obs, p2_obs)

    else:
        discard_hand_card(player_board, discard_board, card)
        update_state_discard(state, card, top_discard, player, p1_obs, p2_obs)

    new_card = draw_new_card(player_board, discard_board, deck, draw_int, top_discard)
    update_state_draw(state, new_card, player, p1_obs, p2_obs, draw_int)

    final_score = player_board.tally_score()

    return final_score - initial_score



