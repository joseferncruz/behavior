# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 16:10:23 2020

@author: Jose Oliveira da Cruz | jose.cruz@nyu.edu
"""


###############################################################################

def plot_distance_speed(
    ax,
    speed,
    distance,
    label_speed,
    label_distance,
    title,
    cs,
    distance_ylim,
):
    """Plot euclidean distance and speed per cs and per epoch."""
    # Plot the speed on the left y axis
    ax.plot(speed, lw=3, label=label_speed, color='darkorange')
    ax.set_ylim(0, 60)
    ax.tick_params('y', colors='darkorange')
    ax.set_ylabel(label_speed, color='darkorange', fontsize=16)
    ax.set_title(f'{title}|{cs}')

    # Plot distance information in the opposite y axis
    ax2 = ax.twinx()
    ax2.plot(distance, lw=3, label=label_distance, color='dodgerblue')
    ax2.set_ylim(distance_ylim)
    ax2.tick_params('y', colors='dodgerblue')
    ax2.set_ylabel(label_distance, color='dodgerblue', fontsize=16)

    # Set xtick labels
    ax.set_xticklabels([a for a in range(0, 31, 5)])
    ax.set_xticks([x for x in range(0, 901, 150)])
    ax.set_xlabel('time (sec)')

###############################################################################

