# -*- coding: utf-8 -*-

"""
Module for creating custom epoch objects
"""

import mne
import scipy.io
import warnings


class EEG_File:
    """
    A class to import and store relevant eeg files

    Attributes:
        folder_path: str
            path to experiment folder
        experiment: str
            the name of the folder containing experiment files
        mat: list of ints
            a list of integers representing impact times
        raw: mne.io.eeglab.eeglab.RawEEGLAB
            raw experiment data in FIF format
    """

    def __init__(self, folder_path, file_name="fixica"):
        """
        Imports and stores EEG data files

        Parameters:
            folder_path: str
                The folder path containing the experiment data
            file_name: str (optional)
                The file name for the .set and .fdt file.
                Defaults to "fixica".
        """

        self.folder_path = folder_path
        self.experiment = folder_path.split("/")[-1]

        try:
            self.mat = scipy.io.loadmat(folder_path+"/impact locations.mat")
        except(FileNotFoundError):
            warnings.warn(
                "Events could not be detected, "
                "please ensure an impact locations.mat file exists"
            )
            # return empty dictionary
            self.mat = dict()

        self.raw = mne.io.read_raw_eeglab(folder_path+"/"+file_name+".set")


class Epochs:
    """
    A class to represent epochs and underlying data

    Attributes:
        eeg_file: EEG_File
            eeg file data
        all_epochs: mne.Epochs
            the generated epoch data
        epoch: mne.Epochs
            the selected epoch of interest

    Methods:
        generate_epochs(duration, start_second):
            Calculates epochs based on a duration and start second
        get_epoch(epoch_num):
            Set and return the epoch of interest
        skip_n_steps(num_steps):
            Returns a subset of the epoch by skipping records in increments of num_steps
    """

    def __init__(
        self,
        folder_path,
        tmin=-0.3,
        tmax=0.7,
        start_second=None,
        file_name="fixica",
        **kwargs
    ):
        """
        Generates epochs and stores related information

        Parameters:
            tmin: float
                Number of seconds before the event time to include in epoch
            tmax: float
                Number of seconds after the event time to include in epoch
            start_second: int | None
                Second of the event time,
                or None if autodetected event time should be used
            file_name: str (optional)
                The file name for the .set and .fdt file.
                Defaults to "fixica".
            **kwargs: dict (optional)
                Additional parameters to pass to the mne.Epochs() constructor

                Full list of options available at
                https://mne.tools/stable/generated/mne.Epochs.html
        """
        if tmax-tmin < 0.0001:
            raise Exception("Please increase the time between tmin and tmax")

        self.eeg_file = EEG_File(folder_path, file_name=file_name)
        self.all_epochs = self.generate_epochs(tmin, tmax, start_second, **kwargs)

        # set first epoch to be the default selection
        self.get_epoch(0)

    def generate_epochs(self, tmin, tmax, start_second, **kwargs):
        """
        Generates an epoch object based on the given input

        Parameters:
            tmin: float
                Number of seconds before the event time to include in epoch
            tmax: float
                Number of seconds after the event time to include in epoch
            start_second: int
                Second of the event time,
                or None if autodetected event time should be used
            **kwargs: dict (optional)
                Additional parameters to pass to the mne.Epochs() constructor

                Full list of options available at
                https://mne.tools/stable/generated/mne.Epochs.html

        Returns:
            mne.Epochs:
                The generated epoch(s)
        """

        # get sampling frequency to convert time steps into seconds
        freq = int(self.eeg_file.raw.info["sfreq"])

        # create epoch with custom event time
        if start_second:
            start_time = start_second*freq
            stim_mock = [[start_time]]

        # create epoch with autodetected event time
        else:
            try:
                stim_mock = self.eeg_file.mat["elecmax1"]
            except(KeyError):
                # if .mat file isn't working set start time to 0
                stim_mock = [[int(-tmin*freq)]]

        # generate the events
        events = [[ts, 0, ts//freq] for i, ts in enumerate(stim_mock[0])]

        # combine default settings with user specified settings
        default_kwargs = {
            "event_id": {str(i[2])+" seconds": i[2] for i in events},
            "tmin": tmin,
            "tmax": tmax,
            "preload": True
        }
        kwargs = {**default_kwargs, **kwargs}

        if tmin == 0:
            kwargs["baseline"] = (0, 0)

        # generate the epoch
        epochs = mne.Epochs(
            self.eeg_file.raw,
            events,
            **kwargs
        )

        return epochs


    def get_epoch(self, epoch_num):
        """
        Get the nth epoch from the genertated epochs

        Parameters:
            epoch_num: int
                The epoch to select
        Returns:
            mne.Epoch:
                The epoch of interest
        """
        if epoch_num > len(self.all_epochs):
            raise Exception(
                "Invalid selection, "
                "epoch_num must be between 0 and "+str(len(self.all_epochs))
            )

        self.epoch = self.all_epochs[epoch_num]
        return self.epoch

    def skip_n_steps(self, num_steps, use_single=True):
        """
        Return new epoch containing every nth frame
        Skips steps between frames

        Parameters:
            num_steps: int
                The number of time steps to skip
            use_single: bool (optional)
                Whether to apply the skipping to all epochs or the
                current selected epoch only

        Returns:
            mne.Epochs:
                The reduced size epoch
        """
        if use_single:
            epochs = self.epoch
        else:
            epochs = self.all_epochs
        return epochs.copy().decimate(num_steps)

    def average_n_steps(self, num_steps):
        """
        Return new epoch containing every nth frame for the selected epoch
        Averages steps bewteen frames

        Parameters:
            num_steps: int
                The number of time steps to average

        Returns:
            mne.Evoked:
                The reduced size epoch in evoked format
        """
        # calculate rolling average one step at a time
        def roll_average(x):
            epoch = x[0]
            arr = epoch*0.0

            for channel in range(epoch.shape[0]):
                for row in range(epoch.shape[1]):
                    arr[channel, row] = epoch[
                        channel,
                        max(row-num_steps//2,0):min(row+num_steps//2+1,epoch.shape[1])
                        ].mean()
            return arr

        # only use every nth average
        epochs = self.epoch
        evoked = epochs.copy().average(method=roll_average).decimate(num_steps)

        # give evoked data the get_data attribute
        # so it can be used in same way as epochs
        setattr(evoked, 'get_data', lambda: evoked.data)

        return evoked
