import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import sys
import os
import re


directory = sys.argv[1]

def make_subplots(plot_type, ax):

    if (plot_type == 'rewards'):
        ylabel = 'Cumulative Rewards'
        yticks = [-40000, -20000, 0, 20000, 40000]
    elif (plot_type == 'scores'):
        ylabel = 'Round Scores'
        yticks = [-150, -100, -50, 0, 50, 100, 150]
    elif (plot_type == 'loss'):
        ylabel = 'Average Batch Loss'
        yticks = [0, 20000, 40000]
    else:
        return

    base_str = 'Rocketman-' + str(plot_type) + '--'
    match = False

    for filename in os.listdir(directory):

        match = re.match(base_str, filename)

        if match:
            arr = np.load(directory + filename)

    arr = arr[:np.count_nonzero(arr)]
    arr_avg = np.convolve(arr, np.ones(100) / 100, mode='valid')

    ax.plot(arr, color='g', alpha=0.3)

    ax.plot(np.arange(100, len(arr_avg) + 100), arr_avg, color='b')

    ax.set_xlabel('Episode')
    ax.set_xticks([0, 200, 400, 600, 800])
    ax.set_ylabel(ylabel)
    ax.set_yticks(yticks)

    return ax


ax0 = plt.subplot2grid((2, 2), (0, 0))
ax0 = make_subplots('rewards', ax0)

ax1 = plt.subplot2grid((2, 2), (0, 1))
ax1 = make_subplots('loss', ax1)

ax2 = plt.subplot2grid((2, 2), (1, 0), colspan=2)
ax2 = make_subplots('scores', ax2)

plt.show()
