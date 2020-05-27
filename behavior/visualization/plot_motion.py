# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 16:10:23 2020

@author: Jose Oliveira da Cruz | jose.cruz@nyu.edu
"""

from tools.utils.organization import fetch_bodypart_coordinates


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


def plot_bodypart_trajectory(
    *,  # Enforce keyword arguments
    ax,
    dataframe,
    bodypart,
    cs_id,
    cs_epoch,
    animal,
):
    """Plot bodypart trajectory.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The ax to plot the data

    dataframe : pandas.DataFrame
        Dataframe generated with function create_bodypart_coord_dataframe().

    bodypart : str
        Bodypart name. Must be in the dataframe columns.

    cs_id : str
        Specific cs (eg 'cs_01')

    cs_epoch : str
        Specifc cs epoch (eg 'peri_cs')

    animal : Animal object
        Containing all the information about the animal as class attributes

    Returns
    -------
    ax : matplotlib.axes.Axes
        Single ax object.
    """
    # Fetch the x, y coordinates for a specific bodypart
    x, y = fetch_bodypart_coordinates(
        dataframe=dataframe,
        bodypart=bodypart,
        cs_id=cs_id,
        cs_epoch=cs_epoch,
    )

    ax.plot(x, y, label=f'{cs_id} | {cs_epoch} | {bodypart}', lw=3)
    ax.invert_yaxis()
    ax.set(ylim=(768, 0),
           xlim=(0, 1024),
           title=f'{animal.experiment_id} | {animal.session} | {animal.sex} | {animal.animal_id}')
    ax.axis('off')
    ax.legend(loc='lower center')

    return ax