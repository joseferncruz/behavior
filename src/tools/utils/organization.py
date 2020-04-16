# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 10:41:58 2020

@author: jfo2
"""

# Dependencies

import pandas as pd
import re
from tools.utils.classAnimal import Animal


##############################################################################


def fetch_animal_info(
    video_key,
    main_record_abs_path,
    experiment_info_abs_path,
):
    """Fetch animal information using animal_id."""
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
