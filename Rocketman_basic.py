import random
import numpy as np
from RocketmanEnv import RocketmanEnv
from find_valid_actions import find_all_valid_actions
from transform_action import pack_action

#-------------------- BRAIN ---------------------------
from keras.models import Sequential
from keras.layers import *
from keras.optimizers import *

from keras import backend as K

import tensorflow as tf

#----------
HUBER_LOSS_DELTA = 1.0
LEARNING_RATE = 0.00025

#----------
def huber_loss(y_true, y_pred):
    err = y_true - y_pred

    cond = K.abs(err) < HUBER_LOSS_DELTA
    L2 = 0.5 * K.square(err)
    L1 = HUBER_LOSS_DELTA * (K.abs(err) - 0.5 * HUBER_LOSS_DELTA)

    loss = tf.where(cond, L2, L1)   # Keras does not cover where function in tensorflow :-(

    return K.mean(loss)


class Brain:
    def __init__(self, stateCnt, actionCnt):
        self.stateCnt = stateCnt
        self.actionCnt = actionCnt

        self.model = self._createModel()
        self.model_ = self._createModel()

        # print self.model.summary()

        self.model.load_weights('Rocketman-network.h5')
        self.model_.load_weights('Rocketman-t_network.h5')


    def _createModel(self):

        model = Sequential()

        model.add(Dense(units=256, activation='relu', input_dim=stateCnt))
        model.add(Dense(512))
        model.add(Dense(units=actionCnt, activation='linear'))

        opt = RMSprop(lr=LEARNING_RATE)
        model.compile(loss=huber_loss, optimizer=opt)

        return model


    def train(self, x, y, epoch=1, verbose=0):

        self.model.fit(x, y, batch_size=256, epochs=epoch, verbose=verbose)


    def predict(self, s, target=False):

        if target:
            return self.model_.predict(s)
        else:
            return self.model.predict(s)

        return self.model.predict(s)


    def predictOne(self, s, target=False):

        return self.predict(s.reshape(1, self.stateCnt), target).flatten()


    def predict_next_action(self, state, player_board, top_discards, target=False):

        valid_actions = find_all_valid_actions(player_board, top_discards)

        next_Qs = self.predictOne(state, target)
        next_Qs = next_Qs[valid_actions]

        idx = np.argmax(next_Qs)

        return valid_actions[idx]


    def updateTargetModel(self):
        self.model_.set_weights(self.model.get_weights())


#-------------------- MEMORY --------------------------
class Memory:   # stored as ( s, a, r, s_ )

    samples = []

    def __init__(self, capacity):

        self.capacity = capacity


    def add(self, sample):

        self.samples.append(sample)        

        if len(self.samples) > self.capacity:
            self.samples.pop(0)


    def sample(self, n):

        n = min(n, len(self.samples))
        return random.sample(self.samples, n)


    def isFull(self):
        return len(self.samples) >= self.capacity



#-------------------- AGENT ---------------------------
MEMORY_CAPACITY = 100000
BATCH_SIZE = 256

GAMMA = 0.99

MAX_EPSILON = 1
MIN_EPSILON = 0.01
LAMBDA = 0.0001      # speed of decay

UPDATE_TARGET_FREQUENCY = 2000

class Agent:

    def __init__(self, stateCnt, actionCnt):

        self.stateCnt = stateCnt
        self.actionCnt = actionCnt

        self.brain = Brain(stateCnt, actionCnt)
        self.memory = Memory(MEMORY_CAPACITY)

        self.steps = 0
        self.epsilon = MAX_EPSILON

        self.rewards_log = np.zeros(25000, dtype=np.int16)
        self.scores_log = np.zeros(25000, dtype=np.int16)

        self.episode = 0


    def act(self, s, player_board, discards):

        hand = player_board.hand

        if random.random() < self.epsilon:

            rand_card = random.choice(hand)

            play = random.choice([0, 1])

            deck_draw = random.choice([0, 1])

            if (deck_draw == 1):
                
                draw_action = 0
            else:

                rand_suit = random.choice([1, 2, 3, 4])

                if (discards[rand_suit-1] == -1):

                    draw_action = 0

                else:

                    draw_action = rand_suit

            return pack_action(rand_card, play, draw_action)

        else:

            return self.brain.predict_next_action(s, player_board, discards)


    def observe(self, sample):  # in (s, a, r, s_) format

        self.memory.add(sample)        

        if (self.steps % UPDATE_TARGET_FREQUENCY == 0):
            self.brain.updateTargetModel()

        # slowly decrease Epsilon based on our eperience
        self.steps += 1
        self.epsilon = MIN_EPSILON + (MAX_EPSILON - MIN_EPSILON) * np.exp(-LAMBDA * self.steps)


    def replay(self):    

        batch = self.memory.sample(BATCH_SIZE)
        batchLen = len(batch)

        no_state = np.zeros(self.stateCnt)

        states = np.array([ o[0] for o in batch ])
        states_ = np.array([ (no_state if o[3] is None else o[3]) for o in batch ])

        p = self.brain.predict(states)
        p_ = self.brain.predict(states_, True)

        x = np.zeros((batchLen, self.stateCnt))
        y = np.zeros((batchLen, self.actionCnt))
        
        for i in range(batchLen):

            obs = batch[i]

            s = obs[0]
            a = obs[1]
            r = obs[2]
            s_ = obs[3]

            target = p[i]

            if s_ is None:
                target[a] = r
            else:
                target[a] = r + GAMMA * np.amax(p_[i])

            x[i] = s
            y[i] = target

        self.brain.train(x, y)


class RandomAgent:
    
    def __init__(self, load_samples):

        self.memory = Memory(MEMORY_CAPACITY)

        if load_samples:
            self.load()


    def act(self, s, player_board, discards):

        hand = player_board.hand

        rand_card = random.choice(hand)

        play = random.choice([0, 1])

        deck_draw = random.choice([0, 1])

        if (deck_draw == 1):
                
            draw_action = 0

        else:

            rand_suit = random.choice([1, 2, 3, 4])

            if (discards[rand_suit-1] == -1):

                draw_action = 0

            else:

                draw_action = rand_suit

        return pack_action(rand_card, play, draw_action)


    def observe(self, sample):  # in (s, a, r, s_) format
        self.memory.add(sample)


    def replay(self):
        pass


    def save(self):

        state_arr = np.zeros((572, MEMORY_CAPACITY))
        action_arr = np.zeros(MEMORY_CAPACITY)
        reward_arr = np.zeros(MEMORY_CAPACITY)
        new_state_arr = np.zeros((572, MEMORY_CAPACITY))

        for i in range(MEMORY_CAPACITY):
            (s, a, r, s_) = self.memory.samples[i]

            state_arr[:, i] = s
            action_arr[i] = a
            reward_arr[i] = r
            new_state_arr[:, i] = s_

        state_filename = 'random_history_state'
        action_filename = 'random_history_action'
        reward_filename = 'random_history_reward'
        new_state_filename = 'random_history_new_state'

        np.save(state_filename, state_arr)
        np.save(action_filename, action_arr)
        np.save(reward_filename, reward_arr)
        np.save(new_state_filename, new_state_arr)


    def load(self):

        state_filename = 'random_history_state.npy'
        action_filename = 'random_history_action.npy'
        reward_filename = 'random_history_reward.npy'
        new_state_filename = 'random_history_new_state.npy'

        state_arr = np.load(state_filename)
        action_arr = np.load(action_filename)
        reward_arr = np.load(reward_filename)
        new_state_arr = np.load(new_state_filename)

        state_arr = state_arr.astype(np.int8)
        action_arr = action_arr.astype(np.int8)
        new_state_arr = new_state_arr.astype(np.int8)

        for i in range(MEMORY_CAPACITY):

            state = state_arr[:, i]
            action = action_arr[i]
            reward = reward_arr[i]
            new_state = new_state_arr[:, i]

            obs = (state, action, reward, new_state)

            self.observe(obs)


#-------------------- ENVIRONMENT ---------------------
class Environment:

    def __init__(self):

        self.env = RocketmanEnv()


    def run(self, agent, logRewards=False):

        self.env.reset()
        done = False

        R = 0 

        while not done:            

            (r, done) = self.run_agent(agent)

            R += r

        if logRewards:

            agent.rewards_log[agent.episode] = R

            cum_score = self.env.gameboard.report_score(1) + self.env.gameboard.report_score(2)
            agent.scores_log[agent.episode] = cum_score

            if ((agent.episode % 200) == 0):
                print 'Episode: ', agent.episode

            agent.episode += 1


    def run_agent(self, agent):

        rewards = [0, 0]
        done_list = [False, False]

        for i in range(2):

            player = i + 1

            if (player == 1):
                state = self.env.p1_obs
                player_board = self.env.gameboard.p1_board

            elif (player == 2):
                state = self.env.p2_obs
                player_board = self.env.gameboard.p2_board

                if (done_list[0]):
                    break

            discards = self.env.top_discard

            s = state.copy()

            a = agent.act(state, player_board, discards)

            (r, done) = self.env.step(a, player)

            if done: # terminal state
                s_ = None
            else:
                s_ = state.copy()

            agent.observe((s, a, r, s_))
            agent.replay()            

            rewards[i] = r
            done_list[i] = done

        R = rewards[0] + rewards[1]
        Done = done_list[0] or done_list[1]

        return (R, Done)


#-------------------- MAIN ----------------------------
env = Environment()

stateCnt  = env.env.observation_space.shape[0]
actionCnt = env.env.action_space.n

print 'State count: ', stateCnt
print 'Action count: ', actionCnt

agent = Agent(stateCnt, actionCnt)

load_random_samples = True

randomAgent = RandomAgent(load_random_samples)

n_games_completed = 0

try:

    while randomAgent.memory.isFull() == False:

        if (n_games_completed % 10 == 0):
            print n_games_completed, ' random games completed'
        n_games_completed += 1

        env.run(randomAgent)

    if not load_random_samples:

        randomAgent.save()

        print 'Random samples saved.'

    agent.memory = randomAgent.memory

    randomAgent = None

    while True:
        env.run(agent, logRewards=True)

finally:

    agent.brain.model.save("Rocketman-network.h5")
    agent.brain.model_.save("Rocketman-t_network.h5")

    np.save('Rocketman-rewards', agent.rewards_log)
    np.save('Rocketman-scores', agent.scores_log)
