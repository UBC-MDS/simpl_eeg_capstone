# -*- coding: utf-8 -*-

"""
Module for creating custom epoch objects
"""

import mne
import scipy.io
import warnings
from os import listdir, walk
from os.path import isfile, join
import numpy as np
import re
import numbers


def load_montage(raw, montage='auto'):
    """
    Helper function for __init__ in EEG_File class that
    loads a montage if one is not set. If no montage
    is specified will try to load an "easycap-M1" montage.
    Returns None if no montage can be loaded.

    Attributes:
        raw: mne.io.eeglab.eeglab.RawEEGLAB
            raw experiment data in FIF format
    """

    # Auto loaded montage exists
    if raw.get_montage():
        # Overwrite automatic montage if one is provided
        if montage != 'auto' and montage != None:
            load_montage=True
        # Use default montage from primary data file
        else:
            load_montage=False
            montage_source = "primary data file"
    
    # If the user does not want a montage loaded
    elif montage == None:
        montage_source = None
        load_montage=False

    # Auto loaded montage does not exist
    else:
        # Load easycap-M1 if no montage is specified
        if montage == 'auto':
            montage == "easycap-M1"
            warnings.warn(
                """No montage has been provided and no montage information
                exists in the primary data file so montage will be set
                to 'easycap-M1' by default (there is no guarantee this will be
                compatible with your data).
                """
            )
        load_montage = True

    if load_montage:
        try:
            mne.channels.make_standard_montage(montage)
            raw.set_montage(montage, verbose=False)
            montage_source = montage
        except:
            warnings.warn(
                """Entered montage type ({}) is not compatible with entered data so no
                montage data has been loaded. Please enter the appropriate montage type
                (https://mne.tools/dev/generated/mne.channels.make_standard_montage.html)
                """.format(montage)
            )
            montage_source = None
        
    return montage_source


def load_events(file_type, raw=None, events_file="auto", folder_path=None):
    """
    Helper function for __init__ in EEG_File class that loads events information.
    Returns events list as first argument and source of events file as the second.
    If the primary data file does not contain events information (.set, .gdf)
    then it loads events for external events file (.mat). If no events_file name is
    provided the alphabetically first .mat file in the folder_path directory which
    is flagged for having less than 5,000 events will be loaded.
    If events exists within the primary data file (.vhdr, .bdf, .edf, .cnt) then
    the will be loaded from it and events_file will be ignored.
    Returns None if no events can be loaded.
    """

    event_load_fail = """Events could not be detected so data has been loaded
    without them. If you wish to load events data please specify a file which
    contains valid events information using the events_file argument."""

    events_file_types = ['.mat']

    events = []
    events_source = None

    if events_file == None:
        warnings.warn(event_load_fail)
        return events, events_source

    #if file_type == '.vhdr' or file_type == '.bdf' or file_type == '.edf' or file_type == '.cnt':
    if events_file == "auto":
        try:
            events, _ = mne.events_from_annotations(raw, verbose=False)
        except:
            events = []

        if (events.shape[0]) > 0:
            events = events.tolist()
            events_source = "primary data file"
            return events, events_source

    if file_type == '.set' or file_type == '.gdf' or file_type == '.nxe':

        events = None
        # Automatically load all files in same directory with events file extension.
        if events_file == 'auto':
            events_file_list = []
            for f in (next(walk(folder_path+"/"), (None, None, []))[2]):
                f_remove=True
                if isinstance(f, str):
                    for f_type in events_file_types:
                        if f.endswith(f_type):
                            f_remove=False
                if f_remove==False:
                    events_file_list.append(f)
            
            # Remove files that don't have events file in last column OR
            # that are flagged with over 5000 events (likely not actually events file) OR
            # that don't possess a numeric value where the first event should be
            for e in events_file_list:
                try:
                    events = scipy.io.loadmat(folder_path+"/"+e)
                    # "events[list(events)[-1]]" gives last column of .mat file which
                    # SHOULD be a list of the events.
                    if (
                        events[list(events)[-1]].shape[1] < 5000 and
                        str(events[list(events)[-1]][0][0]).isnumeric()
                    ):
                        events = events
                        events_file = e
                        break
                except:
                    events = None
        
        try:
            if not events:
                events = scipy.io.loadmat(folder_path+"/"+events_file)
            if (
                events[list(events)[-1]].shape[1] < 5000 and
                str(events[list(events)[-1]][0][0]).isnumeric()
            ):
                stim_mock = events[list(events)[-1]]
                freq = int(raw.info["sfreq"])
                events = [[ts, 0, ts//freq] for i, ts in enumerate(stim_mock[0])]
                events_source = events_file
            else:
                warnings.warn("""
                    Selected events file flagged for having over 5000 events or does not possess
                    events in the right place (should be the final dictionary entry). No events
                    have been loaded."""
                )
                events = []
                events_source = "bad file"
        except(FileNotFoundError):
            warnings.warn(event_load_fail)
            events = []
            events_source = None
        return events, events_source
    
    if file_type == ".cnt":
        warnings.warn(
            """Loading of events has not been implemented for .cnt files.
            No events have been loaded."""
        )
        events = []
        events_source = None
        return events, events_source 
    
    # if file_type == ".mff":
    #     warnings.warn(
    #         """Loading of events has not been implemented for .mff files.
    #         No events have been loaded."""
    #     )
    #     events = []
    #     events_source = None
    #     return events, events_source 

    return events, events_source



def load_file_set(data_path, folder_path, events_file, montage):
    """
    Helper function for __init__ in EEG_File class used to load .set files.
    If some data is stored in a .fdt file in the same directory then it will
    be loaded automatically.
    """
    raw = mne.io.read_raw_eeglab(data_path)
    print("loaded raw from " + data_path)

    events, events_source = load_events(
        '.set', 
        raw=raw, 
        folder_path=folder_path,
        events_file=events_file
    )

    montage_source = load_montage(raw, montage)

    return raw, events, montage_source, events_source


def load_file_vhdr(data_path, montage):
    """
    Helper function for __init__ in EEG_File class used to load .vhdr files.
    """
    raw = mne.io.read_raw_brainvision(data_path)
    print("loaded raw from " + data_path)

    events, events_source = load_events(
        '.vhdr',
        raw=raw
    )

    montage_source = load_montage(raw, montage)

    return raw, events, montage_source, events_source


def load_file_edf(data_path, montage):
    """
    Helper function for __init__ in EEG_File class used to load .edf files.
    """
    raw = mne.io.read_raw_edf(data_path)
    print("loaded raw from " + data_path)

    if '.' in raw.ch_names[0]:
        ch_name_replacement = {}
        for c in raw.ch_names:
            new_name = c.replace(".","").upper().replace("Z","z").replace("FP", "Fp")
            ch_name_replacement[c] = new_name.replace("T9", "FT9").replace("T10", "FT10")
        raw.rename_channels(ch_name_replacement)

    events, events_source = load_events(
        '.edf',
        raw=raw
    )
    
    montage_source = load_montage(raw, montage)

    return raw, events, montage_source, events_source


def load_file_bdf(data_path, montage):
    """
    Helper function for __init__ in EEG_File class used to load .bdf files.
    """
    #NOT PROPERLY TESTED
    # See https://mne.tools/dev/auto_tutorials/io/20_reading_eeg_data.html
    # and https://mne.tools/dev/generated/mne.io.read_raw_bdf.html#mne.io.read_raw_bdf
    # if you wish to properly implement.

    try: 
        raw = mne.io.read_raw_bdf(data_path)
        print("loaded raw from " + data_path)

        events, events_source = load_events(
            '.bdf',
            raw=raw
        )

        montage_source = load_montage(raw, montage)
    except:
        raw = None
        events = None
        montage_source = None
        events_source = None

    return raw, events, montage_source, events_source


def load_file_gdf(data_path, folder_path, events_file, montage):
    """
    Helper function for __init__ in EEG_File class used to load .gdf files.
    """
    #NOT PROPERLY TESTED
    # See https://mne.tools/dev/auto_tutorials/io/20_reading_eeg_data.html
    # and https://mne.tools/dev/generated/mne.io.read_raw_gdf.html#mne.io.read_raw_gdf
    # if you wish to properly implement.

    raw = mne.io.read_raw_gdf(data_path)
    print("loaded raw from " + data_path)

    events, events_source = load_events(
        '.gdf', 
        raw=raw, 
        folder_path=folder_path,
        events_file=events_file
    )

    montage_source = load_montage(raw, montage)

    return raw, events, montage_source, events_source


def load_file_cnt(data_path, montage):
    """
    Helper function for __init__ in EEG_File class used to load .cnt files.
    .cnt files are assumed to contain events
    """
    #NOT PROPERLY TESTED
    # See https://mne.tools/dev/auto_tutorials/io/20_reading_eeg_data.html
    # and https://mne.tools/dev/generated/mne.io.read_raw_cnt.html#mne.io.read_raw_cnt
    # if you wish to properly implement.

    raw = mne.io.read_raw_cnt(data_path)
    print("loaded raw from " + data_path)

    events, events_source = load_events(
        '.cnt', 
        raw=raw
    )

    montage_source = load_montage(raw, montage)

    return raw, events, montage_source, events_source

#.mff files aren't detected for some reason? 
# def load_file_mff(data_path, montage):
#     """
#     Helper function for __init__ in EEG_File class used to load .mff files.
#     """
#     #NOT PROPERLY TESTED
#     # See https://mne.tools/dev/auto_tutorials/io/20_reading_eeg_data.html
#     # and https://mne.tools/dev/generated/mne.io.read_raw_egi.html#mne.io.read_raw_egi
#     # if you wish to properly implement.

#     raw = mne.io.read_raw_egi(data_path)
#     print("loaded raw from " + data_path)

#     events, events_source = load_events(
#         '.mff', 
#         raw=raw
#     )

#     montage_source = load_montage(raw, montage)

#     return raw, events, montage_source, events_source

def load_file_nxe(data_path, folder_path, events_file, montage):
    """
    Helper function for __init__ in EEG_File class used to load eximia (.nxe) files.
    """
    #NOT PROPERLY TESTED
    # See https://mne.tools/dev/auto_tutorials/io/20_reading_eeg_data.html
    # and https://mne.tools/dev/generated/mne.io.read_raw_gdf.html#mne.io.read_raw_gdf
    # if you wish to properly implement.

    raw = mne.io.read_raw_eximia(data_path)
    print("loaded raw from " + data_path)

    events, events_source = load_events(
        '.nxe', 
        raw=raw, 
        folder_path=folder_path,
        events_file=events_file
    )

    montage_source = load_montage(raw, montage)

    return raw, events, montage_source, events_source


def load_file_lay(data_path, folder_path, events_file, montage):
    """
    Helper function for __init__ in EEG_File class used to load eximia (.lay) files.
    """
    #NOT PROPERLY TESTED
    # See https://mne.tools/dev/auto_tutorials/io/20_reading_eeg_data.html
    # and https://mne.tools/dev/generated/mne.io.read_raw_gdf.html#mne.io.read_raw_gdf
    # if you wish to properly implement.

    raw = mne.io.read_raw_eximia(data_path)
    print("loaded raw from " + data_path)

    events, events_source = load_events(
        '.nxe', 
        raw=raw, 
        folder_path=folder_path,
        events_file=events_file
    )

    montage_source = load_montage(raw, montage)

    return raw, events, montage_source, events_source



def load_file_EEG(data_path, folder_path, events_file, montage):
    """
    Helper function for __init__ in EEG_File class used to load Nihon Kohden data
    file (.EEG) files.
    """
    #NOT PROPERLY TESTED
    # See https://mne.tools/dev/auto_tutorials/io/20_reading_eeg_data.html
    # and https://mne.tools/dev/generated/mne.io.read_raw_nihon.html#mne.io.read_raw_nihon
    # if you wish to properly implement.

    raw = mne.io.read_raw_nihon(data_path)
    print("loaded raw from " + data_path)

    # dollar_sign_chs = []
    # for ch in raw.ch_names:
    #     if "$" in ch:
    #         dollar_sign_chs.append(ch)
    # raw.drop_channels(dollar_sign_chs)

    events, events_source = load_events(
        '.EEG', 
        raw=raw, 
        folder_path=folder_path,
        events_file=events_file
    )

    montage_source = load_montage(raw, montage)

    return raw, events, montage_source, events_source




class EEG_File:
    """
    A class to import and store relevant eeg files

    Attributes:
        folder_path: str
            path to experiment folder.
        experiment: str
            the name of the folder containing experiment files.
        mat: list of ints
            a list of integers representing impact times.
        raw: mne.io.eeglab.eeglab.RawEEGLAB
            raw experiment data in FIF format.
    """

    def __init__(self,
                 folder_path,
                 file_name='auto',
                 events_file='auto',
                 montage='auto'):
        """
        Imports and stores EEG data files. Can be used to attach events data from
        an external file if none exists in the primary data. Can be used to load
        a pre-set electrode layout montage.

        Parameters:
            folder_path: str
                The folder path containing the experiment data.
            file_name: str (optional)
                The file name for the primary data file to read in. Should be provided
                as the file name only, with folder_path used to specify a directory.
                If 'auto' is provided then the first alphabetical file name with one
                of the supported file types within the folder_path directory will
                be loaded. The supported and tested filetypes are ".set", ".vhdr"
                and ".edf". Support for ".gdf" and ".cnt" exists but montage's have
                not been successfully loaded in test files. ".bdf', ".nxe", and ".EEG"
                can be imported but events cannot be read.
                Defaults to 'auto'.
            events_file: str (optional)
                The file name for the event file to read in. The supported filetypes
                are ".mat" and ".vmrk". Will only be used if events do not already
                exist in the primary data file. If 'auto' is provided then the first
                alphabetical file in the folder_path direcotry with a supported file
                type will be loaded. If an events file is flagged for containing
                over 5,000 events it's assumed a non-events file was loaded and it
                will be not be loaded, with the second file in alphabetical order
                being loaded instead.
                None can be passed if you do not want to load an events file.
                Defalts to 'auto'.
            montage: str (optional)
                The pre-set montage to load. If a montage already exists in the data
                then providing a montage will overwrite it in the generated data 
                object. If 'auto' is provided and a pre-existing montage exists
                in the data it will be used but if there isn't then the function 
                will try to load an "easycap-M1" montage. A complete list of available
                montages can be found here:
                https://mne.tools/dev/generated/mne.channels.make_standard_montage.html
                None can be passed if you do not want to load a montage.
                Defaults to 'auto'.
        """

        self.folder_path = folder_path
        self.experiment = folder_path.split("/")[-1]
        data_file_type = None
        file_source = None
        events = []
        file_list = []

        # Get a list of all files in the specified folder or put specified file_name into list
        if file_name != None and file_name != 'auto':
            data_path = folder_path+"/"+file_name
            file_source = file_name
            data_file_type = "." + file_name.split('.', 1)[1]

        elif file_name == 'auto':
            # Get list of all files in directory
            file_list = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
            # Keep only strings
            file_list = [ x for x in file_list if isinstance(x, str)]
        # File name is none or invalid
        else:
            data_file_type=None

        file_types = ['.set', '.vhdr', '.edf', '.EDF', '.bdf',
                      '.gdf', '.cnt', '.nxe', '.EEG', '.eeg']
        #Not working (see individual loading functions above): '.mff'

        # If no filename is specified automatically take the first result that matches in the folder
        if file_list:
            for f in file_list:
                for f_type in file_types:
                    if f.endswith(f_type):
                        data_file_type = f_type
                    # If a match has been found save the data_path and break the loop
                        if data_file_type != None:
                            data_path = folder_path+"/"+f
                            file_source = f
                            break

        # Finally, load files and events based on file type
        if data_file_type == '.set':
            raw, events, montage_source, events_source = load_file_set(
                data_path,
                folder_path,
                events_file,
                montage
            )

        elif data_file_type == '.vhdr':
            raw, events, montage_source, events_source = load_file_vhdr(
                data_path, 
                montage
            )
        
        elif data_file_type == '.edf' or data_file_type == '.EDF':
            raw, events, montage_source, events_source = load_file_edf(
                data_path,
                montage
            )
        
        elif data_file_type == '.bdf':
            raw, events, montage_source, events_source = load_file_bdf(
                data_path,
                montage
            )
        
        elif data_file_type == '.gdf':
            raw, events, montage_source, events_source = load_file_gdf(
                data_path,
                folder_path,
                events_file,
                montage
            )
        
        elif data_file_type == '.cnt':
            raw, events, montage_source, events_source = load_file_cnt(
                data_path,
                montage
            )

        # elif data_file_type == '.mff':
        #     raw, events, montage_source, events_source = load_file_mff(
        #         data_path,
        #         montage
        #     )

        elif data_file_type == '.nxe':
            raw, events, montage_source, events_source = load_file_nxe(
                data_path,
                folder_path,
                events_file,
                montage
            )
        
        elif data_file_type == '.EEG':
            raw, events, montage_source, events_source = load_file_EEG(
                data_path,
                folder_path,
                events_file,
                montage
            )

        else:
            raw = None
            events = None
            montage_source = None
            events_source = None
            warnings.warn(
                """No data file could be loaded with from the entered folder_path
                or file_name. Please specify a folder_path containing data with a
                valid EEG data file type {}.""".format(file_types)
            )
        
        #Abandoned feature to set reference since data needs to be pre-loaded for it
        # if raw and ref_channels:
        #     raw.set_eeg_reference(ref_channels=ref_channels)
            
        self.raw = raw
        self.events = events
        self.file_source = file_source
        self.events_source = events_source
        self.montage_source = montage_source

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
            Calculates epochs based on a duration and start second.
        get_epoch(epoch_num):
            Set and return the epoch of interest.
        skip_n_steps(num_steps):
            Returns a subset of the epoch by skipping records in increments of num_steps.
    """

    def __init__(
        self,
        folder_path,
        tmin=-0.3,
        tmax=0.7,
        start_second=None,
        file_name='auto',
        events_file='auto',
        montage='auto',
        **kwargs
    ):
        """
        Generates epochs and stores related information

        Parameters:
            folder_path: str
                The folder path containing the experiment data.
            tmin: float
                Number of seconds before the event time to include in epoch.
            tmax: float
                Number of seconds after the event time to include in epoch.
            start_second: int | None
                Second of the event time,
                or None if autodetected event time should be used
            file_name: str (optional)
                The file name for the primary data file to read in. Should be provided
                as the file name only, with folder_path used to specify a directory.
                If 'auto' is provided then the first alphabetical file name with one
                of the supported file types within the folder_path directory will
                be loaded. The supported and tested filetypes are ".set", ".vhdr"
                and ".edf". Support for ".gdf" and ".cnt" exists but montage's have
                not been successfully loaded in test files. ".bdf', ".nxe", and ".EEG"
                can be imported but events cannot be read.
                Defaults to 'auto'.
            events_file: str (optional)
                The file name for the event file to read in. The supported filetypes
                are ".mat" and ".vmrk". Will only be used if events do not already
                exist in the primary data file. If 'auto' is provided then the first
                alphabetical file in the folder_path direcotry with a supported file
                type will be loaded. If an events file is flagged for containing
                over 5,000 events it's assumed a non-events file was loaded and it
                will be not be loaded, with the second file in alphabetical order
                being loaded instead.
                None can be passed if you do not want to load an events file.
                Defalts to 'auto'.
            montage: str (optional)
                The pre-set montage to load. If a montage already exists in the data
                then providing a montage will overwrite it in the generated data 
                object. If 'auto' is provided and a pre-existing montage exists
                in the data it will be used but if there isn't then the function 
                will try to load an "easycap-M1" montage. A complete list of available
                montages can be found here:
                https://mne.tools/dev/generated/mne.channels.make_standard_montage.html
                None can be passed if you do not want to load a montage.
                Defaults to 'auto'.
            **kwargs: dict (optional)
                Additional parameters to pass to the mne.Epochs() constructor.

                Full list of options available at
                https://mne.tools/stable/generated/mne.Epochs.html
        """
        if tmax-tmin < 0.0001:
            raise Exception("Please increase the time between tmin and tmax")
        
        self.eeg_file = EEG_File(
            folder_path,
            file_name=file_name,
            events_file=events_file,
            montage=montage,
        )
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
            # Make a proper mock events if the type is .set
            events = [[ts, 0, ts//freq] for i, ts in enumerate(stim_mock[0])]

        # create epoch with autodetected event time
        else:
            # If epoch info has been loaded self.events will contain it
            if(self.eeg_file.events):
                events = self.eeg_file.events
            # Else, self.events will be an empty dict
            else:
                # if .mat file isn't working set start time to 0
                stim_mock = [[int(-tmin*freq)]]
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
        if epoch_num == 'evoked':
            self.epoch = self.all_epochs[:].average()

        elif epoch_num > len(self.all_epochs):
            raise Exception(
                "Invalid selection, "
                "epoch_num must be between 0 and "+str(len(self.all_epochs))
            )

        else:
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
