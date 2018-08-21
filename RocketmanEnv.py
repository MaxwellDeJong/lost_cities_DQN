import numpy as np
import gym
from gym import error, spaces, utils
from gym.utils import seeding

from _GameBoard import GameBoard
from _GamePlay import make_move
from transform_action import unpack_action

class RocketmanEnv(gym.Env):

    def __init__(self):

        self.__version__ = "0.0.1"

        self.p1_score = 0
        self.p2_score = 0

        self.gameboard = GameBoard()

        self.action_space = spaces.Discrete(520)
        self.observation_space = spaces.Box(low=0, high=51, shape=(52,), dtype=np.int8)

        self.state = self.initialize_state()

        self.top_discard = -1 * np.ones(4, dtype=np.int8)
        self.flex_options = np.zeros(4, dtype=np.int8)

        self.p1_obs = self.get_observation(1)
        self.p2_obs = self.get_observation(2)


    def initialize_state(self):

        state = np.zeros(52, dtype=np.int8)

        for deck_card in self.gameboard.deck.deckofcards:
            state[deck_card] = 10

        for p1_hand_card in self.gameboard.p1_board.hand:
            state[p1_hand_card] = 0

        for p2_hand_card in self.gameboard.p2_board.hand:
            state[p2_hand_card] = 3

        return state


    def step(self, action_int, player):

        finished = False

        if (player == 1):
            player_board = self.gameboard.p1_board
        else:
            player_board = self.gameboard.p2_board

        action = unpack_action(action_int)

        # Perform a move if there are cards remaining
        if (self.gameboard.cards_remaining != 0):

            score_diff = make_move(player_board, self.gameboard.discard_board, self.gameboard.deck, action, self.state, self.top_discard, self.flex_options, player, self.p1_obs, self.p2_obs)

            if (action[2] == 0):
                self.gameboard.cards_remaining -= 1

            if (self.gameboard.cards_remaining == 0):
                reward = self.gameboard.report_score(player)
            else:
                reward = 0

        # If there aren't cards remaining, calculate the other players score
        else:

            reward = self.gameboard.report_score(player)
            finished = True

        return (reward, finished)


    def reset(self):

        self.gameboard = GameBoard()
        self.initialize_state()

        self.top_discard = -1 * np.ones(4, dtype=np.int8)
        self.flex_options = np.zeros(4, dtype=np.int8)

        self.p1_score = 0
        self.p2_score = 0

        self.p1_obs = self.get_observation(1)
        self.p2_obs = self.get_observation(2)


    def get_observation(self, player):
        '''Denote all cards in the opposing player's hand as well as the deck with state 10.'''

        if (player == 1):
            opp_hand = self.gameboard.p2_board.hand
        elif (player == 2):
            opp_hand = self.gameboard.p1_board.hand

        obs = self.state.copy()

        for card in opp_hand:
            obs[opp_hand] = 10

        return obs


#    def run(self, agent1, agent2):
#
#        self.env.reset()
#        R = 0 
#
#        while True:            
#
#            a = agent.act(s)
#
#            s_, r, done, info = self.env.step(a)
#
#            if done: # terminal state
#                s_ = None
#
#            agent.observe( (s, a, r, s_) )
#            agent.replay()            
#
#            s = s_
#            R += r
#
#            if done:
#                break
#
#        print("Total reward:", R)


