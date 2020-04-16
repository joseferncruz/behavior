# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 10:10:06 2020

@author: Jose Oliveira da Cruz | jose.cruz@nyu.edu
"""



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
            video_key,
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

    def calculate_age(self, date):
        """Calculate the age of the subject at a given date."""
        # Return date in days
        # date = datetime.datetime.strftime(self.date_of_birth)
        pass
