# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 10:41:58 2020

@author: Jose Oliveira da Cruz | jose.cruz@nyu.edu
"""

# Dependencies

import pandas as pd
import re
from tools.utils.classAnimal import Animal
import glob
import os

##############################################################################


def fetch_animal_info(
    video_key,
    main_record_abs_path,
    experiment_info_abs_path,
):
    """Fetch animal information using animal_id.

    Parameters
    ----------
    video_key : str
        Video label following established labelling convention.

    main_record_abs_path : str
        Absolute path to the .csv file containing animal records.

    experiment_info_abs_path : str
        Absolute path to the .csv file containing specific information about
        the experiment.

    Returns
    -------
    animal : instance from Animal Class
        Contains all information as class attributes.
    """
    # Make sure that the key object is a string
    assert isinstance(video_key, str), 'Key must be a string object'

    # Extract information from the key using python regex
    pattern = r'(\w+)_(\w+\d+)_(\d+)_(\w+\d+)_(\w)_(\d+)_(\w\d+)'
    match = re.search(pattern, video_key).groups()

    # Unpack the match object
    user, exp, date, session, species, animal_id, trial = match

    # Read other information from main record
    main_record_dataframe = pd.read_csv(main_record_abs_path,
                                        index_col=0)
    entry = main_record_dataframe[
        main_record_dataframe['animal_id'].isin([animal_id])
    ]

    # Retrive more information from the main_record
    sex = entry.sex.item()
    pi = entry.pi.item()
    date_of_birth = entry.date_of_birth.item()
    strain = str(entry.strain.item())
    species = entry.species.item()
    project = entry.project.item()

    # Read dataframe with experiment info.
    experiment_info_dataframe = pd.read_csv(experiment_info_abs_path,
                                            index_col=0)
    entry = experiment_info_dataframe[
        experiment_info_dataframe['animal_id'].isin([animal_id])
    ]

    # Retrieve remaining information
    experiment_id = entry.exp_id.item()
    session = entry.session.item()
    frame_rate = entry.frame_rate_fps.item()
    cs_start = {col: entry[col].item()
                for col in ['cs_01', 'cs_02', 'cs_03', 'cs_04', 'cs_05']}
    group = entry.treatment.item()
    file_key = video_key
    cs_span_sec = entry.cs_span_sec.item()

    # Instantiate an object from my class Animal
    animal = Animal(
        project,
        pi,
        user,
        species,
        strain,
        animal_id,
        sex,
        date_of_birth,
        experiment_id,
        session,
        frame_rate,
        cs_start,
        cs_span_sec,
        group,
        file_key,
    )
    return animal

###############################################################################


def create_basic_working_record(
        animal,
        n_rows,
):
    """Create basic dataframe with animal details.

    Parameters
    ----------
    animal : object from Animal Class
        Contains the information about specific animals.
    n_rows : int
        Number of rows in the dataframe to return.

    Returns
    -------
    dataframe : DataFrame
    """

    columns = [
        'user', 'exp_id', 'treatment',
        'session', 'species', 'animal_id',
        'age_days', 'weight_grams'
    ]
    dataframe = pd.DataFrame(index=range(n_rows), columns=columns)
    dataframe['user'] = animal.user
    dataframe['exp_id'] = animal.experiment_id
    dataframe['session'] = animal.session
    dataframe['species'] = animal.species
    dataframe['animal_id'] = animal.animal_id
    dataframe['sex'] = animal.sex
    dataframe['age_days'] = animal.age_at_experiment()

    return dataframe

###############################################################################

def concatenate_transformed_dataframes(
        directory_path,
        save_at_directory=False,
):
    """Concatenates dataframes with same columns at specific directory.

    Parameters
    ----------
    directory_path : str
        Absolute path to the directory.

    save_at_directory : bool, optional
        In True, it saves a .csv file with the merged dataframes at the dir.

    Returns
    -------
    merged_dataframes : DataFrame
        All the dataframes merged.

    """
    # Check all the dataframes that exist in the saving directory
    dataframe_filepaths = glob.glob(os.path.join(directory_path,
                                                 '*_individual_summary_stats.csv'))

    # Read all the dataframes and append them to a list
    dataframes_to_merge = [pd.read_csv(filepath, index_col=0)
                           for filepath in dataframe_filepaths]
    # Concatenate all the dataframes together
    merged_dataframes = pd.concat(dataframes_to_merge, ignore_index=True)

    # Save the .csv file at the directory location
    if save_at_directory:
        # Define the basename for the final file
        pattern = '(\w\w_\w+\d+_\d+_\w+\d+_\w_)'

        # Search in the first element of the previous list of paths
        to_match = dataframe_filepaths[0]
        # Find the name using regex
        matched = re.search(pattern, to_match).group()
        final_basename = f'{matched}merged_summary_stats.csv'

        # Absolute saving filepath
        abs_savepath = os.path.join(directory_path, final_basename)

        # Save the dataframe
        merged_dataframes.to_csv(abs_savepath)

        # Confirm success
        print(f'{final_basename} file saved at \n {abs_savepath}')

    return merged_dataframes


###############################################################################

def fetch_bodypart_coordinates(
    *,  # enforce keyword arguments
    dataframe,
    bodypart,
    cs_id,
    cs_epoch,
):
    """Fetch x, y coord from dataframe from create_bodypart_coord_dataframe().

    Parameters
    ----------
    dataframe : pandas DataFrame
        Dataframe with bodypart positions created using the function
        create_bodypart_position_dataframe.
    bodypart : str
        Name of the bodypart must be in the columns from dataframe.
    cs_id : str
        Name of the specific cs.
    cs_epoch : str
        Name of the specific cs epoch.

    Returns
    -------
    x, y : tuple of numpy.ndarray
        Coordinate in pixels for bodypart for a frame during a cs/cs_epoch.
    """
    assert isinstance(bodypart, str), f"{bodypart} must be a string"
    assert isinstance(cs_id, str), f"{cs_id} must be a string"
    assert isinstance(cs_epoch, str), f"{cs_epoch} must be a string"

    # Subset dataframe using cs_id
    target_cs_id = dataframe[dataframe['cs_id'].isin([cs_id])]

    # Subset previous dataframe using cs_epoch
    target_cs_epoch = target_cs_id[target_cs_id['cs_epoch'].isin([cs_epoch])]

    # Assign the x, y coordiates as numpy arrays
    x = target_cs_epoch[f'x_coord_{bodypart}'].to_numpy()
    y = target_cs_epoch[f'y_coord_{bodypart}'].to_numpy()

    return x, y

###############################################################################
