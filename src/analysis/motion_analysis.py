# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 16:17:33 2020

@author: Jose Oliveira da Cruz | jose.cruz@nyu.edu
"""

import pandas as pd
import numpy as np
from scipy.signal import savgol_filter


##############################################################################
def calculate_euclidean_distance(df, convert=False):
    """
    Calculate the euclidean distance between two consecutive x, y coord.

    Returns
    -------
    array with distance values for each CS
    """
    vector_distance = np.array([])

    for index in range(0, len(df)-1):
        x1, y1 = df.iloc[index, 0:2]
        x2, y2 = df.iloc[index+1, 0:2]
        distance = np.sqrt(np.square(x2-x1) + np.square(y2-y1))
        vector_distance = np.append(vector_distance, distance)

    # Convert pix to cm: 28 cm = 330 pix
    if convert:
        vector_distance = (vector_distance*28)/330

    return vector_distance

##############################################################################


def calculate_speed_per_frame(distance_vector, frame_rate):
    """Calculcate a speed vector."""
    speed_vector = distance_vector/(1/frame_rate)
    return speed_vector

##############################################################################


def calculate_euclidean_distance_dataframe(
    dataframe,
    rat,
):
    """Create a dataframe with the euclidean distance for each coord pair."""
    # Extract the list of unique bodyparts
    bodypart_list = list({bodypart
                          for scorer, bodypart, coord in dataframe.columns})

    # Create a dictionary with the bodypart as key,
    # and the x,y,likelihood dataframe as values
    idx = pd.IndexSlice
    dict_df = {bodypart: dataframe.loc[:, idx[:, bodypart]]
               for bodypart in bodypart_list}

    # Calculate the euclideand distance for each body part
    euclidian_dict = {}

    for bodypart in bodypart_list:

        array = calculate_euclidean_distance(dict_df.get(bodypart),
                                             convert=True,
                                             )
        euclidian_dict.setdefault(bodypart)

        # Instantiate dictionary to save the euclidian distances per cs
        cs_array_dict = {}

        for cs, cs_start in rat.cs_start.items():  # Loops through all the cs

            cs_array_dict.setdefault(cs)

            # Slice the corresponding cs epoch:
            # 60 seconds before cs_start : 90 seconds after
            start = int(cs_start - (60*rat.frame_rate))
            end = int(cs_start + (90*rat.frame_rate))

            # Interpolate the array to correspond to 30fps of aquisition rate.
            # real aquisition rate
            old_length = np.linspace(start, end, num=(end-start), endpoint=True)
            # new aquisition rate: 30 frames per second during 30 seconds
            new_length = np.linspace(start, end, num=(150*30), endpoint=True)
            x = new_length
            xp = old_length
            fp = array[start:end]

            # Interpolate
            yinterp = np.interp(x, xp, fp)

            # Add the interpolation to the cs key
            cs_array_dict[cs] = yinterp

        # Add the results from each cs to the bodypart key
        euclidian_dict[bodypart] = cs_array_dict

    # Instantiate the DataFrame
    columns = [
        'user', 'exp_id', 'treatment',
        'session', 'species', 'animal_id',
        'session', 'cs_id', 'cs_epoch'
    ]
    number_cs = len(rat.cs_start.keys())
    dataframe_final = pd.DataFrame(index=np.arange(1, 4500*number_cs+1),
                                   columns=columns)

    # Build the final dataframe to return
    for bodypart in bodypart_list:
        counter = 1
        for cs, cs_start in rat.cs_start.items():
            # cs = 'cs_01'
            # cs_start = cs_index.get('cs_01')

            # Update dataframe
            start = counter
            end = counter+4499

            # Add the ed_bodypart to the dataframe_final
            dataframe_final.loc[start:end, f'ed_{bodypart}'] = euclidian_dict.get(bodypart).get(cs)
            dataframe_final.loc[start:end, 'cs_id'] = cs

            # Conplete info
            dataframe_final.loc[start:end, 'user'] = rat.user
            dataframe_final.loc[start:end, 'exp_id'] = rat.experiment_id
            dataframe_final.loc[start:end, 'session'] = rat.session
            dataframe_final.loc[start:end, 'species'] = rat.species
            dataframe_final.loc[start:end, 'animal_id'] = rat.animal_id

            # Discriminate the cs_epoch
            dataframe_final.loc[start:start+1800, 'cs_epoch'] = 'pre_cs'
            dataframe_final.loc[start+1800:start+2700, 'cs_epoch'] = 'peri_cs'
            dataframe_final.loc[start+2700:end, 'cs_epoch'] = 'post_cs'
            counter += 4500

    return dataframe_final, euclidian_dict


###############################################################################

def calculate_speed_dataframe(
    dataframe,
    bodyparts_list,
    frame_rate,
):
    """Calculate the speed using the euclidean distance points."""
    # Copy the dataframe to not edit the original.
    final_dataframe = dataframe.copy()

    for bodypart in bodyparts_list:

        speed_bodypart = calculate_speed_per_frame(
            final_dataframe[f'ed_{bodypart}'], frame_rate
            )

        final_dataframe[f'speed_{bodypart}'] = speed_bodypart

    return final_dataframe


###############################################################################

def extract_speed_distance_from_dataframe(
        dataframe,
        bodypart,
        cs,
        epoch,
):
    """Extract speed and distance from interm dataframe."""
    # Extract data for chosen cs
    cond_cs_id = dataframe['cs_id'] == cs

    # Extract data from chosen cs_epoch
    if epoch == 'pre_cs':
        epoch = dataframe['cs_epoch'] == 'pre_cs'
    elif epoch == 'peri_cs':
        epoch = dataframe['cs_epoch'] == 'peri_cs'
    elif epoch == 'post_cs':
        epoch = dataframe['cs_epoch'] == 'post_cs'
    else:
        print('epoch choosen not valid.')

    cum_sum_ed = np.cumsum(dataframe[cond_cs_id][epoch][f'ed_{bodypart}']
                           ).reset_index(drop=True).to_numpy()

    # Ensure to return an array of len(900)
    if len(cum_sum_ed) == 900:
        cum_sum_ed = cum_sum_ed - cum_sum_ed[0]
    else:
        cum_sum_ed = cum_sum_ed[-900:] - cum_sum_ed[-900]

    # speed data
    speed = dataframe[cond_cs_id][epoch][f'speed_{bodypart}']
    speed = savgol_filter(speed, window_length=9, polyorder=1)

    # Ensure to return an array of len(900)
    if len(speed) != 900:
        speed = speed[-900:]

    return speed, cum_sum_ed

###############################################################################


def extract_darting_events(
    speed_array,
    distance_array,
    threshold_speed,
    threshold_distance,
):
    """Extract darting events based on the speed and cumulative distance."""
    # Extract the indices where speed > threshold
    running = []
    final = []
    for index in range(len(speed_array)):
        if speed_array[index] > threshold_speed:
            running.append(index)
        else:
            final.append(running)
            running = []

    final = [list_ for list_ in final if list_]  # Remove empty lists

    # Using the previous indices, check where
    # the cumulative sum of the distance is above threshold
    final_event_index = []
    counter = 1  # Keep track of the events

    for list_ in final:
        cum_sum_distance = np.cumsum(distance_array[list_])[-1]  # last value

        # Apend the lists of indices that meet the criteria
        if cum_sum_distance > threshold_distance:
            final_event_index.append((counter, list_))
            counter += 1

    # Create an array with the len of the orinal speed array with value==0
    array_to_return = np.zeros([len(speed_array), 1], dtype=int)

    for index, list_ in final_event_index:
        # detected events are labelled with the value 1
        array_to_return[list_] = 1

    return array_to_return.reshape(len(array_to_return)), final_event_index

###############################################################################


def calculate_threshold(arr, factor):
    """Return the threshold of the signal based on the mean and std."""
    threshold = round(np.mean(arr) + factor*np.std(arr))
    return threshold

###############################################################################
