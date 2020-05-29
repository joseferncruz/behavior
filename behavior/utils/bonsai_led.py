# -*- coding: utf-8 -*-
"""
Behavior - 2020 - LeDoux Lab

Licensed under GNU Lesser General Public License v3.0

@author: Jose Oliveira da Cruz | jose.cruz@nyu.edu
"""
# Import modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import re

##############################################################################


def detect_bonsai_led_state(
    bonsai_csv,
    factor,
    CS_number,
    output_directory,
):
    """DOC."""
    final_answer = "N"
    while final_answer != "Y":

        # Open bonsai output with the LED area
        bonsai_df = pd.read_csv(bonsai_csv,
                                names=["timestamp", "LED_AREA"],
                                date_parser="timestamp",
                                )
        bonsai_df["cs_state"] = 0  # LED: 1==ON, 0==OFF
        # Set baseline and threshold for detection of LED ON
        baseline = bonsai_df["LED_AREA"].mean()  # CS == OFF
        threshold = baseline*factor

        # keep track of led behavior(on, off) in each frame
        led_state_array = np.array([])

        # Loop through all the frames to detect flurescence area
        for frame in bonsai_df.index:
            # detect LED OFF: CS==0
            if bonsai_df['LED_AREA'][frame] < threshold:
                led_state_array = np.append(led_state_array, 0)
            # detect LED ON: CS==1
            else:
                led_state_array = np.append(led_state_array, 1)

        frame = 0
        CS_frame = []

        # Extract the frame where the led is ON
        while frame < len(led_state_array):
            # detection of the CS ON
            if led_state_array[frame] == 1:
                CS_frame.append(frame)  # append the index
                # move forward 900 frames in order to detect the next event
                frame += 900
            else:
                frame += 1

        # remove all cs falsely detected.
        if len(CS_frame) > CS_number:
            answer = 'N'  # user input about the detection
            while answer != "Y":
                # Plot LED area in pixels over frames.
                fig, ax = plt.subplots(figsize=(20, 5))

                ax.plot(bonsai_df.index, bonsai_df["LED_AREA"])
                ax.set_ylabel('LED_AREA (pixels)')
                ax.set_xlabel('frame_index')
                ax.set_ylim(0, bonsai_df['LED_AREA'].max())

                # Add the cs number on the plot
                for cs in CS_frame:
                    ax.annotate(s=str(cs),
                                xy=(cs, bonsai_df['LED_AREA'].max()),
                                xycoords='data',
                                xytext=(cs+1, bonsai_df['LED_AREA'].min()),
                                arrowprops=dict(facecolor='black', shrink=0.05),
                                )
                plt.show()

                print("Write the frame index number (single frame): ",
                      CS_frame)

                frame_to_remove = int(input("insert the frame number: "))

                while True:
                    if frame_to_remove in CS_frame:
                        CS_frame.remove(frame_to_remove)
                        break
                    else:
                        continue

                print(CS_frame)
                answer = str(input("Are you done? (Y/N)")).upper()
        else:
            pass

        # plot the newly extracted frames
        fig, ax = plt.subplots(figsize=(20, 5))
        ax.set_title('Final Extraction')
        ax.plot(bonsai_df.index, bonsai_df["LED_AREA"], color='orange')
        ax.set_ylabel('LED_AREA (pixels)')
        ax.set_xlabel('frame_index')
        ax.set_ylim(0, bonsai_df['LED_AREA'].max())

        # Add the cs number on the plot
        for cs in CS_frame:
            ax.annotate(s=str(cs),
                        xy=(cs, bonsai_df['LED_AREA'].max()),
                        xycoords='data',
                        xytext=(cs+1, bonsai_df['LED_AREA'].min()),
                        arrowprops=dict(facecolor='black', shrink=0.05),
                       )
        plt.show()

        final_answer = str(input("do you validade this extraction? (Y/N)").upper())

    # save file here
    # Use regular expression to find the base name
    pattern = re.compile(r'\w+_\w+\d+_\d+_\w+\d+_\w_\d+_\w\d+.csv')
    base_name = re.search(pattern, bonsai_csv).group().replace('.csv',
                                                               "_CS-INDEX.txt",
                                                               )

    cs_index_saving_path = os.path.join(output_directory, base_name)

    with open(cs_index_saving_path, "w") as file:
        file.write(str(CS_frame))
    print(f"Extraction done, cs indices saved at: {cs_index_saving_path}")
    return bonsai_df

##############################################################################


def merge_extracted_cs_indices(directory, session):
    """DOC STRING."""
    # Access all the files in the directory
    files_to_process = [file for file in os.listdir(directory)
                        if file.endswith('CS-INDEX.txt')]

    pattern = re.compile(r'_\w\w\w\d\d_')
    files_to_process = [file for file in files_to_process
                        if re.search(pattern, file).group() == session]

    # generate the dataframe where all the data will be pulled together

    df = pd.DataFrame(columns=['user', 'exp_id', 'date', 'session',
                               'species', 'animal_id', 'cs_01',
                               'cs_02', 'cs_03', 'cs_04', 'cs_05'],
                      index=range(len(files_to_process)),
                      )
    # extract experiment id files
    for index, file in enumerate(files_to_process):

        # Extract information from animal_key
        user = file.split("_")[0].lower()
        exp_id = file.split("_")[1].lower()
        date = file.split("_")[2]
        session = file.split("_")[3].lower()
        species = file.split("_")[4].lower()
        if species == 'r':
            species = 'rat'
        elif species == 'm':
            species = 'mouse'
        animal_id = file.split("_")[5]

        # open the file and extract the cs indices
        with open(os.path.join(directory, file), "r") as cs_indices:
            cs_indices = cs_indices.read()
            cs_indices = cs_indices.replace("[", "").replace("]", "").split(", ")

        # merge all the data together
        row_to_append = ([user, exp_id, date, session, species, animal_id]
                         + cs_indices)

        # append to the dataframe
        df.iloc[index, :] = row_to_append

    return df

##############################################################################


def calculate_frame_rate(
        directory,
        session,
):
    """DOC STRING."""
    # Use regex to filter files of interest in the directory
    pattern = re.compile(r'_\w\w\w\d\d_')
    directory_files = [file for file in os.listdir(directory)
                       if file.endswith('.csv')]

    directory_files = [file for file in directory_files
                       if re.search(pattern, file).group() == session]

    main_dataframe = pd.DataFrame(index=range(len(directory_files)),
                                  columns=['animal_id', 'frame_rate_fps'])

    for index, file in enumerate(directory_files):

        # Read timestamps
        full_path = os.path.join(directory, file)
        df = pd.read_csv(full_path,
                         names=["timestamp", "LED_AREA"],
                         parse_dates=True)

        # transform the timestamp into datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=False)

        # Create a timedelta object repreesented in seconds
        df['timestamp'] = pd.to_timedelta(df['timestamp'].dt.strftime('%H:%M:%S')
                                          ).dt.total_seconds().astype(int)

        # Create a timedelta with the first timestamp
        df["net_timestamp"] = df["timestamp"] - df["timestamp"][0]

        # Create an additional column representing each frame as the int 1
        # (to be used to count the number of frames in each second)
        df["frames_count"] = np.ones(len(df))

        # Group by "timestamp" (== each second) column
        # and sum all the frames in each grouped second
        df_1 = df.groupby("timestamp").sum()

        # Append to the main dataframe
        animal_id = file.split('_')[5]
        mean_frame_rate = round(df_1["frames_count"].mean(), 2)
        main_dataframe.iloc[index, :] = [animal_id, mean_frame_rate]

    return main_dataframe

##############################################################################
