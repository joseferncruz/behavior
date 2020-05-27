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

    Parameters
    ----------
    df : pandas.DataFrame
        data output from deeplabcut

    convert : bool, optional
        Convert pixel to cm: 28 cm = 330 pix

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
    convert=True,
):
    """Create a dataframe with the euclidean distance for each coord pair.

    Parameters
    ----------
    dataframe : pandas.DataFrame

    rat : rat object

    convert : bool, optional
        Convert pix to cm: 28 cm = 330 pix

    Returns
    -------
    dataframe_final
    euclidian_dict
    """
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
                                             convert=convert,
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


def group_darting_events(dataframe):
    """Group darting events for each cs in pre, peri and post-cs epochs.

    The function uses the dataframe and data

    """
    darting_events = []
    running_index = []
    counter = 1
    for index, element in enumerate(dataframe['darting_events']):
        if element == 1:
            running_index.append(index)
        else:
            darting_events.append((counter, running_index))
            counter += 1
            running_index = []

    # Remove empty lists
    darting_events = [list_ for index, list_ in darting_events if list_]

    darting_per_cs_epoch = {
        'pre_cs': 0,
        'peri_cs': 0,
        'post_cs': 0,
    }
    # Devide the findings in pre, peri and post-cs
    for list_ in darting_events:
        # pre-cs
        if list_[0] < 900:
            darting_per_cs_epoch['pre_cs'] += 1
        elif list_[0] > 900 & list_[0] < 1800:
            darting_per_cs_epoch['peri_cs'] += 1
        else:
            darting_per_cs_epoch['post_cs'] += 1

    return darting_per_cs_epoch


###############################################################################


def calculate_mean_darting(dataframe):
    """Calculate mean darting events during pre, peri and post_cs epochs."""
    # Create shell dataframe
    df = pd.DataFrame(columns=[
        'cs_id', 'cs_epoch', 'darting_raw', 'darting_norm', 'darting_events'
        ]
    )
    # Extract unique cs_ids
    cs_id_list = dataframe.cs_id.unique()

    for cs_id in cs_id_list:
        # access the specific cs
        condition = dataframe['cs_id'].isin([cs_id])

        # Extract the relevant time points and cs epochs
        individual_cs = dataframe[condition]

        individual_cs = individual_cs[['cs_epoch', 'cs_id', 'darting_events']
                                      ].reset_index(drop=True).iloc[900:3600]

        # Calculate the overall darting and add it to the dataframe
        darting = individual_cs.groupby(['cs_epoch']).sum().reset_index()
        darting.columns = ['cs_epoch', 'darting_raw']
        darting['cs_id'] = cs_id

        # Normalize to the total epoch bin time (30 seconds, 900 frames)
        darting['darting_norm'] = darting['darting_raw'
                                          ].agg(lambda x: x/900
                                                ).agg(lambda x: round(x, 2)
                                                      )

        # Extracting the number of darting events and merge with the dataframe
        darting_per_cs_epoch = pd.Series(group_darting_events(individual_cs),
                                         ).reset_index()
        darting = darting.merge(darting_per_cs_epoch,
                                left_on='cs_epoch',
                                right_on='index',
                                ).drop('index', axis=1)
        darting.rename(columns={0: 'darting_events'}, inplace=True)

        # Append to the dataframe to return
        df = df.append(darting)

    df.reset_index(inplace=True, drop=True)

    return df

###############################################################################


def calculate_distance_per_cs_epoch(
        dataframe,
        bodypart='ed_back_head',
        units='cm',
):
    """Calculate distance for each cs, cs_epoch based on specific bodypart."""
    df = pd.DataFrame(columns=[
            'cs_id', 'cs_epoch', f'total_distance_{units}',
            ]
        )

    for cs_id in dataframe['cs_id'].unique():
        condition = dataframe['cs_id'].isin([cs_id])

        # Extract the relevant time points and cs epochs
        individual_cs = dataframe[condition]

        individual_cs = individual_cs[['cs_epoch', 'cs_id', bodypart]
                                      ].reset_index(drop=True).iloc[900:3600]

        # Distance covered during each cs_epoch
        total_distance = individual_cs.groupby(['cs_epoch']
                                               ).sum().agg(lambda x: round(x, 2)
                                                           ).reset_index()

        total_distance.rename(columns={bodypart: f'total_distance_{units}'},
                              inplace=True)

        # Add cs_id
        total_distance['cs_id'] = cs_id

        # Append to the dataframe to return
        df = df.append(total_distance).reset_index(drop=True)

    return df

###############################################################################


def calculate_mean_speed_per_epoch(
        dataframe,
        bodypart='speed_back_head',
        units='cm/sec',
):
    """Calculate the mean speed during pre, peri and post cs."""
    df = pd.DataFrame(columns=[
            'cs_id', 'cs_epoch', f'mean_speed_{units}',
            ]
        )

    for cs_id in dataframe['cs_id'].unique():

        condition = dataframe['cs_id'].isin([cs_id])

        # Extract the relevant time points and cs epochs
        individual_cs = dataframe[condition]

        individual_cs = individual_cs[['cs_epoch', 'cs_id', bodypart]
                                      ].reset_index(drop=True).iloc[900:3600]

        # Calculate mean speed during each cs_epoch
        speed = individual_cs.groupby(['cs_epoch']
                                      ).mean().agg(lambda x: round(x, 2)
                                                   ).reset_index()

        speed.rename(columns={bodypart: f'mean_speed_{units}'}, inplace=True)

        # Add cs_id
        speed['cs_id'] = cs_id

        # Append to the dataframe to return
        df = df.append(speed).reset_index(drop=True)
    return df

###############################################################################

def create_bodypart_coord_dataframe(
        dataframe,
        rat,
):
    """Create a datafrme with each x, y bodypart position and
    corrects the aquisition rate to 30 fps.

    Parameters
    ----------
    dataframe : DataFrame
        The raw dataframe from deeplabcut output.

    rat : Animal object
        Instance of the Animal class with all the necessary information

    Returns
    -------
    dataframe : DataFrame
        Dataframe with x, y bodypart coordinate per cs,
        per cs_epoch with Animal information.

    """
    # Extract the list of unique bodyparts from deeplabcut raw dataframe
    bodypart_list = list({bodypart
                          for scorer, bodypart, coord in dataframe.columns})

    # Create a dictionary with the bodypart as key,
    # and the x, y deeplabcut dataframe as values
    idx = pd.IndexSlice
    dict_bodypart_dataframes = {bodypart: dataframe.loc[:, idx[:, bodypart, ['x', 'y']]]
                                for bodypart in bodypart_list}

    # Part 1 - Loop the bodyparts, extract each x, y position
    # during each cs and correct the aquisition (to 30fps)
    bodypart_coord_dict = {}
    for bodypart in bodypart_list:

        cs_array_dict = {}
        for cs, cs_start in rat.cs_start.items():  # Loops through all the cs

            # For each coordinate
            coord_dict = {}
            for coord in ['x', 'y']:

                # Slice the corresponding cs epoch:
                # 60 seconds before cs_start : 90 seconds after
                start = int(cs_start - (60*rat.frame_rate))  # pre-cs
                end = int(cs_start + (90*rat.frame_rate))    # post-cs start

                # Interpolate the data to correct from aquisition rate to 30fps.
                # original data
                data_points = dict_bodypart_dataframes.get(bodypart).loc[start:end, idx[:, :, coord]].to_numpy()

                # real aquisition rate
                old_length = np.linspace(start,
                                         end,
                                         num=len(data_points),
                                         endpoint=True,
                                         )

                # new aquisition rate: 30 frames per second
                # during 150 seconds (ie 60+90)
                new_length = np.linspace(start,
                                         end,
                                         num=(150*30),
                                         endpoint=True,
                                         )

                # numpy interp function arguments
                x = new_length
                xp = old_length
                fp = data_points.squeeze()
                # Interpolate
                yinterp = np.interp(x, xp, fp)

                # Add the coordinate interpolation to dictionary
                coord_dict.update({coord: yinterp})

            # Add the x, y interpolations as values to cs_id as key
            cs_array_dict.setdefault(cs, coord_dict)
        # for each bodypart, assing the dictionary
        # containing all the cs and corresponsing x, y positions
        bodypart_coord_dict.setdefault(bodypart, cs_array_dict)

    # Part 2 - Build the dataframe to return

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

            # Update dataframe
            start = counter
            end = counter+4499

            # Add the ed_bodypart to the dataframe_final
            for coord in ['x', 'y']:
                coord_data = bodypart_coord_dict.get(bodypart).get(cs).get(coord)
                dataframe_final.loc[start:end, f'{coord}_coord_{bodypart}'] = coord_data

            dataframe_final.loc[start:end, 'cs_id'] = cs
            # Conplete info with animal object information
            dataframe_final.loc[start:end, 'user'] = rat.user
            dataframe_final.loc[start:end, 'exp_id'] = rat.experiment_id
            dataframe_final.loc[start:end, 'session'] = rat.session
            dataframe_final.loc[start:end, 'species'] = rat.species
            dataframe_final.loc[start:end, 'animal_id'] = rat.animal_id

            # Discriminate the cs_epoch
            dataframe_final.loc[start:start+1800, 'cs_epoch'] = 'pre_cs'
            dataframe_final.loc[start+1800:start+2700, 'cs_epoch'] = 'peri_cs'
            dataframe_final.loc[start+2700:end, 'cs_epoch'] = 'post_cs'

            # move to the next cs_id
            counter += 4500

    return dataframe_final

###############################################################################

