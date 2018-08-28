#--- enable this to run on GPU
# import os    
# os.environ['THEANO_FLAGS'] = "device=gpu,floatX=float32"  

import random
import numpy as np
from RocketmanEnv import RocketmanEnv
from find_valid_actions import find_all_valid_actions
from transform_action import pack_action

#-------------------- BRAIN ---------------------------
from keras.models import Sequential
from keras.layers import *
from keras.optimizers import *

class Brain:
    def __init__(self, stateCnt, actionCnt, player):
        self.stateCnt = stateCnt
        self.actionCnt = actionCnt

        self.model = self._createModel()

        print self.model.summary()

        #self.model.load_weights('Rocketman-basic-' + str(player) + '.h5')


    def _createModel(self):

        model = Sequential()

        model.add(Dense(units=256, activation='relu', input_dim=stateCnt))
        model.add(Dense(512))
        model.add(Dense(units=actionCnt, activation='linear'))

        opt = RMSprop(lr=0.00025)
        model.compile(loss='mse', optimizer=opt)

        return model


    def train(self, x, y, epoch=1, verbose=0):

        self.model.fit(x, y, batch_size=256, epochs=epoch, verbose=verbose)


    def predict(self, s):

        return self.model.predict(s)


    def predictOne(self, s):

        return self.predict(s.reshape(1, self.stateCnt)).flatten()


    def predict_next_action(self, state, player_board, top_discards):

        valid_actions = find_all_valid_actions(player_board, top_discards)

        next_Qs = self.predictOne(state)
        next_Qs = next_Qs[valid_actions]

        idx = np.argmax(next_Qs)

        return valid_actions[idx]


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

class Agent:

    def __init__(self, stateCnt, actionCnt, player):

        self.stateCnt = stateCnt
        self.actionCnt = actionCnt

        self.brain = Brain(stateCnt, actionCnt, player)
        self.memory = Memory(MEMORY_CAPACITY)

        self.steps = 0
        self.epsilon = MAX_EPSILON

        self.player = player

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
        p_ = self.brain.predict(states_)

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
    
    def __init__(self, player, load_samples):

        self.player = player

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

        state_filename = 'random_history_state_' + str(self.player)
        action_filename = 'random_history_action_' + str(self.player)
        reward_filename = 'random_history_reward_' + str(self.player)
        new_state_filename = 'random_history_new_state_' + str(self.player)

        np.save(state_filename, state_arr)
        np.save(action_filename, action_arr)
        np.save(reward_filename, reward_arr)
        np.save(new_state_filename, new_state_arr)


    def load(self):

        state_filename = 'random_history_state_' + str(self.player) + '.npy'
        action_filename = 'random_history_action_' + str(self.player) + '.npy'
        reward_filename = 'random_history_reward_' + str(self.player) + '.npy'
        new_state_filename = 'random_history_new_state_' + str(self.player) + '.npy'

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


    def run(self, agent1, agent2, logRewards=False):

        self.env.reset()
        done = False

        R1 = 0 
        R2 = 0 

        while not done:            

            (r1, done) = self.run_agent(agent1, 1)
            (r2, done) = self.run_agent(agent2, 2)

            R1 += r1
            R2 += r2

        if logRewards:

            agent1.rewards_log[agent1.episode] = R1
            agent2.rewards_log[agent2.episode] = R2

            agent1.scores_log[agent1.episode] = self.env.gameboard.report_score(1)
            agent2.scores_log[agent2.episode] = self.env.gameboard.report_score(2)

            if ((agent1.episode % 200) == 0):
                print 'Episode: ', agent1.episode

            agent1.episode += 1
            agent2.episode += 1


    def run_agent(self, agent, player):

        if (player == 1):
            state = self.env.p1_obs
            player_board = self.env.gameboard.p1_board
        elif (player == 2):
            state = self.env.p2_obs
            player_board = self.env.gameboard.p2_board

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

        return (r, done)


#-------------------- MAIN ----------------------------
env = Environment()

stateCnt  = env.env.observation_space.shape[0]
actionCnt = env.env.action_space.n

print 'State count: ', stateCnt
print 'Action count: ', actionCnt

agent1 = Agent(stateCnt, actionCnt, 1)
agent2 = Agent(stateCnt, actionCnt, 2)

load_random_samples = False

randomAgent1 = RandomAgent(1, load_random_samples)
randomAgent2 = RandomAgent(2, load_random_samples)

x = 0

try:

    while randomAgent1.memory.isFull() == False:

        if (x % 10 == 0):
            print x, ' random games completed'
        x += 1

        env.run(randomAgent1, randomAgent2)

    if not load_random_samples:

        randomAgent1.save()
        randomAgent2.save()

        print 'Random samples saved.'

    agent1.memory = randomAgent1.memory
    agent2.memory = randomAgent2.memory

    randomAgent1 = None
    randomAgent2 = None

    while True:
        env.run(agent1, agent2, logRewards=True)

finally:

    agent1.brain.model.save("Rocketman-basic-1.h5")
    agent2.brain.model.save("Rocketman-basic-2.h5")

    np.save('Rocketman-log-1', agent1.rewards_log)
    np.save('Rocketman-log-2', agent2.rewards_log)

    np.save('Rocketman-scores-1', agent1.rewards_log)
    np.save('Rocketman-scores-2', agent2.rewards_log)
