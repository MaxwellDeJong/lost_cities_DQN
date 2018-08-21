def generate_hot_one_vector(card_list):
    '''Generates a hot-one encoded vector from a list of cards.'''

    hot_one_vec = np.zeros(52, dtype=np.int8)

    suit_list = ['c', 'd', 'h', 's']
    face_list = ['a', 'j', 'q', 'k', '2', '3', '4', '5', '6', '7', '8', '9', '10']

    idx = 0

    for suit in suit_list:
        for face_val in face_list:

            card = suit + face_val

            if card in card_list:

                hot_one_vec[idx] = 1

            idx += 1

    return hot_one_vec


def process_played_cards(board, played):
    '''Generates a hot-one encoded vector from lists for the played cards of each suit.'''

    if played:

        clubs = board.played_clubs
        diamonds = board.played_diamonds
        hearts = board.played_hearts
        spades = board.played_spades

    else:

        clubs = board.clubs_discarded
        diamonds = board.diamonds_discarded
        hearts = board.hearts_discarded
        spades = board.spades_discarded

    hot_one_vec = np.zeros(52, dtype=np.int8)

    suit_list = ['c', 'd', 'h', 's']
    face_list = ['a', 'j', 'q', 'k', '2', '3', '4', '5', '6', '7', '8', '9', '10']

    all_played_cards = [clubs, diamonds, hearts, spades]

    idx = 0

    for played_suit in all_played_cards:

        for card in played_suit:

            if (card[1] in face_list):
                hot_one_vec[idx] = 0

            idx += 1

    return hot_one_vec

