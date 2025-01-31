import numpy as np
import gym
from gym import error, spaces, utils
from gym.utils import seeding

from _GameBoard import GameBoard
from _GamePlay import make_move
from transform_action import unpack_action
from transform_state import get_idx
from calculate_reward_function import calc_max_reward


class RocketmanEnv(gym.Env):

    def __init__(self):

        self.__version__ = "0.0.1"

        self.gameboard = GameBoard()

        self.action_space = spaces.Discrete(520)
        self.observation_space = spaces.Box(low=0, high=1, shape=(572,), dtype=np.int8)

        self.state = self.initialize_state()

        self.top_discard = -1 * np.ones(4, dtype=np.int8)
        self.flex_options = np.zeros(4, dtype=np.int8)

        self.p1_obs = self.get_observation(1)
        self.p2_obs = self.get_observation(2)


    def initialize_state(self):

        state_vec = np.zeros(572, dtype=np.int8)

        for deck_card in self.gameboard.deck.deckofcards:

            state = 10

            idx = get_idx(deck_card, state)
            state_vec[idx] = 1

        for p1_hand_card in self.gameboard.p1_board.hand:

            state = 0

            idx = get_idx(p1_hand_card, state)
            state_vec[idx] = 1

        for p2_hand_card in self.gameboard.p2_board.hand:

            state = 3

            idx = get_idx(p2_hand_card, state)
            state_vec[idx] = 1

        return state_vec


    def step(self, action_int, player):

        finished = False

        if (player == 1):
            player_board = self.gameboard.p1_board
        else:
            player_board = self.gameboard.p2_board

        action = unpack_action(action_int)

        # Perform a move if there are cards remaining
        if (self.gameboard.cards_remaining != 0):

            make_move(player_board, self.gameboard.discard_board, self.gameboard.deck, action, self.state, self.top_discard, self.flex_options, player, self.p1_obs, self.p2_obs)

            if (action[2] == 0):
                self.gameboard.cards_remaining -= 1

            if (self.gameboard.cards_remaining == 0):
                reward = self.gameboard.report_score(player)
            else:

                reward = calc_max_reward(self.gameboard, player)

        # If there aren't cards remaining, calculate the other players score
        else:

            reward = self.gameboard.report_score(player)
            finished = True

        return (reward, finished)


    def reset(self):

        self.gameboard = GameBoard()
        self.state = self.initialize_state()

        self.top_discard = -1 * np.ones(4, dtype=np.int8)
        self.flex_options = np.zeros(4, dtype=np.int8)

        self.p1_obs = self.get_observation(1)
        self.p2_obs = self.get_observation(2)


    def get_observation(self, player):
        '''Denote all cards in the opposing player's hand as well as the deck with state 10.'''

        if (player == 1):
            opp_hand = self.gameboard.p2_board.hand
            state_to_hide = 3

        elif (player == 2):
            opp_hand = self.gameboard.p1_board.hand
            state_to_hide = 0

        obs = self.state.copy()
        hidden_state = 10

        for card in opp_hand:

            hide_idx = get_idx(card, state_to_hide)
            new_idx = get_idx(card, hidden_state)

            obs[hide_idx] = 0
            obs[new_idx] = 1

        return obs
