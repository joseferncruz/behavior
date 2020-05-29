# -*- coding: utf-8 -*-
"""
Behavior - 2020 - LeDoux Lab

Licensed under GNU Lesser General Public License v3.0

@author: Jose Oliveira da Cruz | jose.cruz@nyu.edu
"""

import pandas as pd
import numpy as np
from scipy.signal import savgol_filter




##############################################################################

def calculate_mean_freezing(dataframe):
    """Mean freezing per cs, per cs_epoch."""
    # Instantiate dataframe
    df = pd.DataFrame(columns=[
        'cs_id', 'cs_epoch', 'freezing_raw', 'freezing_norm',
        ]
    )

    # Extract unique cs_ids
    cs_id_list = dataframe.cs_id.unique()

    for cs_id in cs_id_list:
        # access the specific cs
        condition = dataframe['cs_id'].isin([cs_id])

        # Extract the relevant time points and cs epochs
        individual_cs = dataframe[condition]

        individual_cs = individual_cs[['cs_epoch', 'cs_id', 'freezing_events']
                                      ].reset_index(drop=True).iloc[900:3600]

        # Calculate the overall freezing and add it to the dataframe
        freezing = individual_cs.groupby(['cs_epoch']).sum().reset_index()
        freezing.columns = ['cs_epoch', 'freezing_raw']
        freezing['cs_id'] = cs_id

        # Normalize to the total epoch bin time (30 seconds, 900 frames)
        freezing['freezing_norm'] = freezing['freezing_raw'
                                             ].agg(lambda x: x/900
                                                   ).agg(lambda x: round(x, 2)
                                                         )

        # Append to the dataframe to return
        df = df.append(freezing)

    df.reset_index(inplace=True, drop=True)

    return df

##############################################################################


def extract_freezing_events(
        dataframe,
        bodyparts,
        motion_threshold,
        min_freezing_duration,
):
    """Calculate freezing events using euclidean distance."""
    # Part A: Detect freezing events
    # Relabel bodyparts to use as dataframe index
    bodyparts = [f'ed_{bodypart}' for bodypart in bodyparts]

    # Calculate in which timepoint the euclidean distance in between points
    # was bellow the threshold (==freezing). Use cumulative product to
    # make sure all bodyparts were bellow threshold
    freezing_events = (dataframe[bodyparts] < motion_threshold).cumprod(axis=1)

    # transform the result in a numpy array
    freezing_events = freezing_events.iloc[:, -1].to_numpy()

    # Part B: Filter freezing events to consider only if
    #         time bin is >= 15 (half-second)

    running = []
    final = []
    event_counter = 1
    for index in range(len(freezing_events)):
        if freezing_events[index] > 0:
            running.append(index)
        else:
            final.append((event_counter, running))
            running = []
            event_counter += 1

    # Remove freezing events that are bellow minimum freezing threshold
    final = [events for counter, events in final
             if len(events) >= min_freezing_duration]

    # Build new array with filtered events
    freezing_array_to_return = np.zeros(len(freezing_events), dtype=int)
    for element in final:
        freezing_array_to_return[element] = 1

    return freezing_array_to_return

###############################################################################
# LEGACY
##############################################################################


def extract_freezing_events_legacy(
    dataframe,
    bodyparts,
    motion_threshold,
):
    """Calculate freezing events using euclidean distance."""
    # Relabel bodyparts to use as dataframe index
    bodyparts = [f'ed_{bodypart}' for bodypart in bodyparts]

    # Calculate in which timepoint the euclidean distance in between points
    # was bellow the threshold (==freezing). Use cumulative product to
    # make sure all bodyparts were bellow threshold
    freezing_events = (dataframe[bodyparts] < motion_threshold).cumprod(axis=1)

    # transform the result in a numpy array
    freezing_events = freezing_events.iloc[:, -1].to_numpy()

    return freezing_events
