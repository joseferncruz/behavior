# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 10:10:06 2020

@author: Jose Oliveira da Cruz | jose.cruz@nyu.edu
"""

import datetime
import re

class Animal():
    """Create a class to hold attributes of individual animal """
    def __init__(
            self,
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
            video_key=None,
    ):

        self.project = project
        self.user = user
        self.pi = pi
        self.species = species
        self.strain = strain
        self.animal_id = animal_id
        self.sex = sex
        self.date_of_birth = str(date_of_birth)
        self.experiment_id = experiment_id
        self.session = session
        self.frame_rate = frame_rate
        self.cs_start = cs_start
        self.cs_span_sec = cs_span_sec
        self.group = group
        self.video_basename = video_key

    def age_at_experiment(self):
        """Return the age in days of the subject at the experiment date."""
        if self.video_basename is None:
            print('There is no video_basename to extract the date.')
            pass
        else:
            # Parse datetime of birth
            date_of_birth = datetime.datetime.strptime(self.date_of_birth,
                                                       '%Y%m%d',
                                                       )

            # Search in the video_basename the date of experiment
            pattern = r'(\d\d\d\d\d\d\d\d)'  # yyyymmdd
            experiment_date = re.search(pattern, self.video_basename).group()
            date = datetime.datetime.strptime(experiment_date, '%Y%m%d')

            return (date - date_of_birth).days
