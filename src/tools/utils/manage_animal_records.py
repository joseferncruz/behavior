"""
author = josecruz
jose.cruz@nyu.edu or josecruz.cbr@gmail.com

"""
# Import modules
import pandas as pd
import numpy as np
import os
import time


##############################################################################
def create_new_animal_record(
    animal_list=[],
    project=None,
    PI=None,
    user=None,
    species=None,
    strain=None,
    age_at_arrival_weeks=None,
    sex=None,
    date_of_birth=None,
    date_of_arrival=None,
    location_id=None
):
    """Create a new animal record.

    Parameters
    ----------
    arg_1 : str
        <description>
    arg_2 : bool, optional
        <description>

    Returns
    -------
    dataframe
        dataframe with all animals and respective information in a panel
    """

    column_labels = ["project", "pi", "user",
                     "species", "strain", "animal_id",
                     "sex", "date_of_birth", "date_of_arrival",
                     "age_at_arrival_weeks", "location_id",
                     ]
    # Create the shape of the dataframe.
    animal_record = pd.DataFrame(index=np.arange(len(animal_list)),
                                 columns=column_labels,
                                 )
    animal_list_sorted = sorted(animal_list)

    # Loop through every animal in the list and add it to the dataframe.
    for animal in range(len(animal_list_sorted)):
        animal_record.iloc[animal, 5] = animal_list_sorted[animal]
        animal_record["project"] = project
        animal_record["pi"] = PI
        animal_record["user"] = user
        animal_record["species"] = species
        animal_record["strain"] = strain
        animal_record["age_at_arrival_weeks"] = age_at_arrival_weeks
        animal_record["sex"] = sex
        animal_record["date_of_birth"] = date_of_birth
        animal_record["date_of_arrival"] = date_of_arrival
        animal_record["location_id"] = location_id

    return animal_record

##############################################################################


def update_main_record(
    new_animal_record,
    animal_record_to_update,
    save_output=None
):
    """Update an existing animal record.

    Parameters
    ----------
    new_animal_record : dataframe
        <description>

    animal_record_to_update : dataframe
        <description>

    save_path : str, optional

    Returns
    -------
    dataframe
        dataframe with all animals and respective information in a panel
    """
    # Merge records.
    merged_records = pd.concat([animal_record_to_update,
                                new_animal_record])
    # Save file.
    if save_output is not None:
        file_name = 'main_record_{}.csv'.format(time.strftime('%Y%m%d_%H%M%S'))
        saving_path = os.path.join(save_output, file_name)
        merged_records.to_csv(saving_path)
        print(f'File saved at {saving_path}')

    return merged_records

##############################################################################


def save_animal_record(
    animal_record,
    save_dir,
    save_csv=True,
    save_excel=False,
):
    """Save animal record.

    Parameters
    ----------
    animal_record : dataframe
        DataFrame with the record to be saved.

    save_dir : str
        Filepath where the file is intended to be stored.

    save_csv: bool, optional
        Save file as .csv

    save_excel: bool, optional
        Save file as .xls

    Returns
    -------


    """
    if save_csv:
        save_csv_path = os.path.join(save_dir,
                                     'new_import_{}.csv'.format(
                                         time.strftime("%Y%m%d_%H%M%S")
                                         )
                                     )
        animal_record.to_csv(save_csv_path)
        print(f'File saved at {save_csv_path}.')

    if save_excel:
        save_excel_path = os.path.join(save_dir,
                                       'new_import_{}.xls'.format(
                                           time.strftime("%Y%m%d_%H%M%S")
                                           )
                                       )
        animal_record.to_excel(save_excel_path)
        print(f'File saved at {save_excel_path}.')

##############################################################################


def get_main_record(
    main_record_dir,
):
    """Get the latest main record from folder.

    Parameters
    ----------
    arg : dataframe
        <description>


    save_path : str, optional

    Returns
    -------


    """
    # Check directory
    latest_main_record = os.listdir(main_record_dir)[-1]

    # Verify if there are main_record_files
    if latest_main_record.startswith('main_record'):
        # Get the file path.
        main_record_filepath = os.path.join(main_record_dir,
                                            latest_main_record,
                                            )
        # Get the dataframe.
        main_record = pd.read_csv(main_record_filepath, index_col=0)

        return (main_record_filepath, main_record)
    else:
        print('There is no main_record in this folder.')

##############################################################################
