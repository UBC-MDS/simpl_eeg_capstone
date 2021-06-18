# -*- coding: utf-8 -*-

"""
Module for generating and animating EEG connectivity figures
"""

import mne
import scipy.io
import warnings


class EEG_File:
    """
    A class to import and store relevant eeg files

    Attributes:
        folder_path : str
            path to experiment folder
        experiment : str
            the name of the folder containing experiment files
        mat : list of ints
            a list of integers representing impact times
        raw : mne.io.eeglab.eeglab.RawEEGLAB
            raw experiment data in FIF format
    """

    def __init__(self, folder_path, file_name="fixica"):
        """
        Imports and stores EEG data files

        Parameters:
            folder_path : str
                The folder path containing the experiment data
            file_name : str (optional)
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
        eeg_file : EEG_File
            eeg file data
        data : mne.Epochs
            the generated epoch data
        epoch : mne.Epochs
            the selected epoch

    Methods:
        generate_epochs(duration, start_second):
            Calculates epochs based on a duration and start second
        set_nth_epoch(epoch_num):
            Set the epoch of interest
        get_nth_epoch(epoch_num):
            Retrieves the nth epoch
        get_frame(tmin, step_size, frame_number):
            Calculates a subset of the epoch based on the step size and frame
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
            tmin : float
                Number of seconds before the event time to include in epoch
            tmax : float
                Number of seconds after the event time to include in epoch
            start_second : int | None
                Second of the event time,
                or None if autodetected event time should be used
            file_name : str (optional)
                The file name for the .set and .fdt file.
                Defaults to "fixica".
            **kwargs : dict (optional)
                Additional parameters to pass to the mne.Epochs() constructor

                Full list of options available at
                https://mne.tools/stable/generated/mne.Epochs.html
        """
        if tmax-tmin < 0.0001:
            raise Exception("Please increase the time between tmin and tmax")

        self.eeg_file = EEG_File(folder_path, file_name=file_name)
        self.data = self.generate_epochs(tmin, tmax, start_second, **kwargs)
        self.set_nth_epoch(0)

    def generate_epochs(self, tmin, tmax, start_second, **kwargs):
        """
        Generates an epoch object based on the given input

        Parameters:
            tmin : float
                Number of seconds before the event time to include in epoch
            tmax : float
                Number of seconds after the event time to include in epoch
            start_second : int
                Second of the event time,
                or None if autodetected event time should be used
            **kwargs : dict (optional)
                Additional parameters to pass to the mne.Epochs() constructor

                Full list of options available at
                https://mne.tools/stable/generated/mne.Epochs.html

        Returns:
            mne.Epochs:
                The generated epoch
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

    def set_nth_epoch(self, epoch_num):
        """
        Set the nth epoch from the raw data

        Parameters:
            epoch_num : int
                The epoch to select
        """

        self.epoch = self.data[epoch_num]

    def get_nth_epoch(self, epoch_num=None):
        """
        Return the nth epoch from the raw data,
        or current selected epoch if epoch_num is not given

        Parameters:
            epoch_num : int
                The epoch to select
        Returns:
            mne.Epoch:
                The epoch of interest
        """

        if epoch_num:
            self.set_nth_epoch(epoch_num)
        return self.epoch

    def skip_n_steps(self, num_steps):
        """
        Return new epoch containing every nth frame

        Parameters:
        num_steps : int
            The number of time steps to skip

        Returns:
            mne.Epochs:
                The reduced size epoch
        """

        return self.epoch.copy().decimate(num_steps)
