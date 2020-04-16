# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 16:17:33 2020

@author: Jose Oliveira da Cruz | jose.cruz@nyu.edu
"""

import pandas as pd
import numpy as np
from scipy.signal import savgol_filter


##############################################################################


def extract_freezing_events(
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


##############################################################################

