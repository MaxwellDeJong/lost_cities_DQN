import numpy as np
import matplotlib.pyplot as plt

R1 = np.loadtxt('Rocketman-log-1.npy')
R1 = R1[:np.count_nonzero(R1)]

R1_avg = np.convolve(R1, np.ones(100) / 100, mode='valid')

plt.plot(R1, color='g', alpha=0.3)
plt.plot(np.arange(100, len(R1) + 100), R1_avg, color='b')

plt.xlabel('Episode')
plt.ylabel('Cumulative Rewards')

plt.show()

scores1 = np.loadtxt('Rocketman-scores-1.npy')
scores1 = scores1[:np.count_nonzero(scores1)]

scores1_avg = np.convolve(scores1, np.ones(100) / 100, mode='valid')

plt.plot(scores1, color='g', alpha=0.3)
plt.plot(np.arange(100, len(scores1) + 100), scores1_avg, color='b')

plt.xlabel('Episode')
plt.ylabel('Round Score')

plt.show()
