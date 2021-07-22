import streamlit as st
import streamlit.components.v1 as components

import numpy as np
import mne

import os
from os import walk

from simpl_eeg import (
    eeg_objects,
    raw_voltage,
    connectivity,
    topomap_2d,
    topomap_3d_brain,
    topomap_3d_head
)

import matplotlib.pyplot as plt
import re
import datetime
import time
import pickle
import scipy.io

SECTION_NAMES = {
    "raw": "Raw Voltage Values",
    "2d_head": "2D Head Map",
    "3d_head": "3D Head Map",
    "3d_brain": "3D Brain Map",
    "connectivity": "Connectivity",
    "connectivity_circle": "Connectivity Circle"
}

SPINNER_MESSAGE = "Rendering..."
DEFAULT_FRAME_RATE = 12.0

DATA_FOLDER = "data/"
HEADER_EPOCH_PATH = "src/pre_saved/epoch_info"
HEADER_FWD_PATH = "src/pre_saved/forward"

st.set_page_config(
    page_title="SimPL EEG App",
    page_icon="docs/simpl_instructions/logo.png",
    layout="wide"
)

st.markdown(
    """
    <style>
        .streamlit-expanderHeader{font-size:120%;}
    </style>
    """,
    unsafe_allow_html=True
)

def format_kwargs_list(**kwargs):
    """Helper function to format kwargs for printing"""
    args = []
    for i in kwargs:
        value = kwargs[i]
        if type(value) == str:
            value = f"'{value}'"
        elif type(value) == np.ndarray:
            value = [list(i) for i in value]
        args.append(f"{i}={value}")
    return args

def format_code(func, **kwargs):
    """Helper function to format code for printing"""
    extra_params = format_kwargs_list(**kwargs)

    all_params = ", \n\t".join(["epoch"] + extra_params)
    code = f"{func.__module__}.{func.__name__}(\n\t{all_params}\n)"
    return code


@st.cache(show_spinner=False)
def calculate_timeframe(start_time, raw):
    """
    Parse time from string and determine position in raw data

    Parameters:
        start_time : str
            The start time in format H:M:S
        raw : mne.io.Raw
            The full experiment data

    Returns:
        tuple of length 2:
            The time in seconds and a string indicating whether the timestamp
            is within the epoch's timeframe or not.
    """
    if re.match('^[0-9]{1,}:[0-9]{1,}:[0-9]{1,}$', start_time):
        start = datetime.datetime.strptime(start_time, '%H:%M:%S')
        zero = datetime.datetime.strptime('0:00:00', '%H:%M:%S')
        seconds = (start-zero).total_seconds()
        if re.match('^0{1,}:0{1,}:0{1,}$', start_time):
            # Timestamp is zero
            in_timeframe = "min"
        elif seconds < 0:
            in_timeframe = "negative"
        elif seconds > raw.times[-1]:
            # Timestamp exceeds max time
            in_timeframe = "exceeds"
        elif (raw.times[-1] - seconds) < 1:
            # Timestamp matches max time
            in_timeframe = "max"
        else:
            in_timeframe = "yes"
        # return start second, and whether or not in timeframe
        return int(seconds), in_timeframe
    else:
        # No start time, timstamp in wrong timeframe
        return None, "wrong_format"


@st.cache(show_spinner=False)
def files_with_specific_extension(experiment_num, file_types):
    """
    Helper function for building list of files in experiment directory.
    """
    file_list = []
    for f in (next(walk("data/"+experiment_num+"/"), (None, None, []))[2]):
        f_remove=True
        for f_type in file_types:
            if f.endswith(f_type):
                f_remove=False
        if f_remove==False:
            file_list.append(f)

    file_list.insert(0, 'None')
    file_list.insert(0,'auto')
    

    return file_list.copy()


@st.cache(show_spinner=False)
def generate_fwd(epoch):
    """
    Helper function for 3D brain map - Generate forward solution from epoch
    """
    return(topomap_3d_brain.create_fsaverage_forward(epoch))


@st.cache(show_spinner=False)
def generate_stc(epoch, fwd):
    """
    Helper function for 3D brain map
    generates inverse solution from forward and epoch
    """
    return(topomap_3d_brain.create_inverse_solution(epoch, fwd))


def render_raw_voltage_plot(epoch, **kwargs):
    """
    Caching wrapper function to call topomap_2d.animate_topomap_2d
    """
    func = raw_voltage.plot_voltage
    plot = func(epoch, **kwargs)
    code = format_code(func, **kwargs)
    return plot, code


@st.cache(show_spinner=False)
def animate_ui_2d_head(epoch, **kwargs):
    """
    Caching wrapper function to call topomap_2d.animate_topomap_2d
    """
    func = topomap_2d.animate_topomap_2d
    anim = func(epoch, **kwargs)
    code = format_code(func, **kwargs)
    return anim.to_jshtml(), code


@st.cache(show_spinner=False)
def animate_ui_3d_head(epoch, **kwargs):
    """
    Caching wrapper function to call topomap_3d_head.animate_3d_head
    """
    func = topomap_3d_head.animate_3d_head
    anim = func(epoch, **kwargs)
    code = format_code(func, **kwargs)
    return anim, code


@st.cache(show_spinner=False)
def animate_ui_3d_brain(**kwargs):
    """
    Caching wrapper function to call
    topomap_3d_brain.animate_matplot_brain
    """
    func = topomap_3d_brain.animate_matplot_brain
    anim = func(**kwargs)
    code = format_code(func, **kwargs)
    return anim.to_jshtml(), code


@st.cache(show_spinner=False)
def animate_ui_connectivity(epoch, **kwargs):
    """
    Caching wrapper function to call connectivity.animate_connectivity
    """
    if kwargs.get('sphere') == None:
        kwargs.pop('sphere', None)
    print(kwargs)
    func = connectivity.animate_connectivity
    anim = func(epoch, **kwargs)
    code = format_code(func, **kwargs)
    return anim.to_jshtml(), code


@st.cache(show_spinner=False)
def animate_ui_connectivity_circle(epoch, **kwargs):
    """
    Caching wrapper function to call
    connectivity.animate_connectivity_circle
    """
    func = connectivity.animate_connectivity_circle
    anim = func(epoch, **kwargs)
    code = format_code(func, **kwargs)
    return anim.to_jshtml(), code


@st.cache(show_spinner=False)
def get_axis_lims(epoch):
    """
    Generates an invisible mne.viz.plot_topomap plot and gets the ylim from its
    matplotlib.axes._subplots.AxesSubplot.
    
    Parameters:
        epoch: mne.epochs.Epochs
            MNE epochs object containing the timestamps.
        
    Returns:
        ax_lims: tuple
            A tuple of the ax_lims.
    """
    fig, ax = plt.subplots()

    if type(epoch) is mne.evoked.EvokedArray:
        plot_data = epoch.data[:, 0]
    else:
        plot_data = epoch.get_data('eeg')[0][:, 0] 
    
    mne.viz.plot_topomap(
        data=plot_data,
        pos=epoch.info,
        show=False,
        res=1
    )
    
    axis_lims = ax.get_ylim()
    plt.close()
    return(axis_lims)


@st.cache(show_spinner=False)
def generate_event_times_only(events):
    """
    Helper function for creating standalone eeg_file object
    """
    event_times_only = []
    for i in events:
        event_times_only.append(i[0])
    event_times_only = np.array(event_times_only)
    return event_times_only


@st.cache(show_spinner=False)
def check_if_sphere_works(epoch, extrapolate_setting):
    """
    Helper function for creating standalone eeg_file object
    """
    if type(epoch) is mne.evoked.EvokedArray:
        plot_data = epoch.data[:, 0]
    else:
        plot_data = epoch.get_data('eeg')[0][:, 0]  

    can_use_sphere_param=True
    try:
        mne.viz.plot_topomap(
            data=plot_data,
            pos=epoch.info,
            extrapolate=extrapolate_setting,
            sphere=100,
            res=1,
            show=False
        )
    except:
        can_use_sphere_param=False
    return(can_use_sphere_param)


@st.cache(show_spinner=False)
def generate_eeg_raw(experiment_num, **kwargs):
    """
    Helper function used to create raw eeg file. This file is
    never used to generate any figures in the UI but is used 
    to display stats and perform dynamic checks.
    """
    if kwargs.get('file_name') == 'None':
        kwargs.pop('file_name', None)
        kwargs['file_name'] = None
    if kwargs.get('events_file') == 'None':
        kwargs.pop('events_file', None)
        kwargs['events_file'] = None
    if kwargs.get('montage') == 'None':
        kwargs.pop('montage', None)
        kwargs['montage'] = None

    gen_eeg_file = eeg_objects.EEG_File(
        DATA_FOLDER+experiment_num,
        **kwargs
    )
    return gen_eeg_file


@st.cache(show_spinner=False)
def remove_bad_events_files(events_file_list, experiment_num):
    """
    Helper function used to remove files accidentaccidentallyaly flagged as event files
    """
    for check_event in events_file_list:
        remove_event=False
        if check_event.endswith(".mat"):
            loaded_event = scipy.io.loadmat("data/"+experiment_num+"/"+check_event)
            try:
                if loaded_event[list(check_event)[-1]].shape[1] > 5000:
                    remove_event=True
                if str(events[list(events)[-1]][0][0]).isnumeric() == False:
                    remove_event=True
            except:
                remove_event=True

        if remove_event==True:
            events_file_list.remove(check_event)


@st.cache(show_spinner=False)
def generate_epoch(experiment_num, epoch_num, **kwargs):
    """
    Generate a custom epoch

    Parameters:
        experiment_num : str
            Folder name of experiment
        tmin : float
            Seconds before the event time
        tmax : float
            Seconds after the event time
        start_second : int
            The second of event
        epoch_num : int (optional)
            An epoch of interest to store.

    Returns:
        eeg_objects.Epoch:
            The generated epoch object
    """

    if kwargs.get('file_name') == 'None':
        kwargs.pop('file_name', None)
        kwargs['file_name'] = None
    if kwargs.get('events_file') == 'None':
        kwargs.pop('events_file', None)
        kwargs['events_file'] = None
    if kwargs.get('montage') == 'None':
        kwargs.pop('montage', None)
        kwargs['montage'] = None

    epoch_obj = eeg_objects.Epochs(
        DATA_FOLDER+experiment_num,
        **kwargs
    )
    epoch_obj.get_epoch(epoch_num)
    return epoch_obj


@st.cache(show_spinner=False, suppress_st_warning=True)
def get_shared_conn_widgets(epoch, frame_steps, key):
    """
    Helper function for producing shared widgets for
    connectivity sections
    """

    key = str(key)

    connectivity_methods = [
        "correlation",
        "spectral_connectivity",
        "envelope_correlation",
    ]

    if (len(epoch.times)//frame_steps) >= 100:
        connectivity_methods.append("covariance")

    label = "Select connection calculation"
    connection_type = st.selectbox(
        label,
        connectivity_methods,
        key=label+key,
        format_func=lambda name: name.replace("_", " ").capitalize(),
        help="""Calculation type, one of
        spectral connectivity, envelope correlation,
        covariance, correlation.
        Envelope correlation is only available with 100 or more timesteps
        per frame.
        """
    )
    default_cmin = -1.0
    default_cmax = 1.0
    if(connection_type == "envelope_correlation"):
        default_cmin = 0.0

    label = "Minimum Value"
    cmin = st.number_input(
        label,
        value=default_cmin,
        key=label+key,
        help="The minimum for the scale."
    )

    label = "Maximum Value"
    cmax = st.number_input(
        label,
        value=default_cmax,
        min_value=cmin,
        key=label+key,
        help="The maximum for the scale"
    )

    return connection_type, cmin, cmax


def get_f_rate_widget(key):
    """
    Helper function for producing shared widgets for
    frame rate adjusters
    """
    f_rate_widget = st.number_input(
        "Animation frame rate (fps)",
        value=DEFAULT_FRAME_RATE,
        min_value=1.0,
        help="""The frame rate that the animation will play at in frames per second.
        Setting higher values will make the animation play faster.""",
        key=key
    )
    
    return f_rate_widget


def get_working_montage(experiment_num, montage_list, file_name, return_first_match):
    """
    Prints a list of working montages for the given 
    """
    montage_options=[]

    for try_montage in montage_list[2:]:
        test_montage = generate_eeg_raw(
            experiment_num,
            montage = try_montage
        )
        if test_montage.montage_source != None:
            if return_first_match == True:
                return try_montage
            else:
                montage_options.append(try_montage)
    
    if bool(montage_options) == False and return_first_match:
        montage_options = None
    
    return montage_options


def get_list_of_files_cache(path):
    """
    Helper for load_generate_fwd. Gets list of files in a file path
    with the extension ".pickle" and returns a list of them
    """
    file_list = []
    for f in (next(walk(path), (None, None, []))[2]):
        f_remove=True
        if f.endswith(".pickle"):
            f_remove=False
        if f_remove==False:
            file_list.append(f)
    
    return file_list

def load_generate_fwd(
    plot_epoch,
    forward_genearted,
    experiment_num,
    HEADER_EPOCH_PATH,
    HEADER_FWD_PATH):
    """
    Load fwd from the fwd cache or generate a new one and put it into the cache
    """
    # Fetch cache of epoch_info's
    pre_load_epoch_list = get_list_of_files_cache(HEADER_EPOCH_PATH)

    # Fetch cache of fwd's
    pre_load_fwd_list = get_list_of_files_cache(HEADER_FWD_PATH)

    try:
        if type(plot_epoch) == mne.epochs.Epochs:
            # Loads example epochs from cache, checks if it's 'epoch.info' matches the
            # current plot_epoch. If it does, loads pre-exisiting forward to save time.
            if forward_genearted is False:
                for e in pre_load_epoch_list:
                    with open(HEADER_EPOCH_PATH+'/'+e, "rb") as loaded_epoch:
                        example_epoch_info = pickle.load(loaded_epoch)
                    d1 = dict(plot_epoch.info)
                    d1.pop("chs",0)
                    example_epoch_info.pop("chs", 0)
                    if d1 == example_epoch_info:
                        FILE_LEAD = e.split("_epoch_info.pickle")[0]
                        FWD_FILE = HEADER_FWD_PATH + '/' + FILE_LEAD + "_fwd.pickle"
                        with open(FWD_FILE, "rb") as loaded_fwd:
                            fwd = pickle.load(loaded_fwd)
                            if type(fwd) == mne.forward.forward.Forward:
                                forward_genearted = True
                                print('loaded')
                                break

            # If no matching epoch.info found in cache then make fwd and save it + curent epoch info
            # to the custom cache
            if forward_genearted is False:
                fwd = generate_fwd(plot_epoch)
                forward_genearted = True
                epoch_info_file_name = HEADER_EPOCH_PATH + '/' + experiment_num + "_epoch_info.pickle"
                with open(epoch_info_file_name, 'wb') as handle:
                    epoch_info_dict = dict(plot_epoch.info)
                    pickle.dump(epoch_info_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
                pre_load_epoch_list.append(experiment_num + "_epoch_info.pickle")
                fwd_file_name = HEADER_FWD_PATH + '/' + experiment_num + "_fwd.pickle"
                with open(fwd_file_name, 'wb') as handle:
                    pickle.dump(fwd, handle, protocol=pickle.HIGHEST_PROTOCOL)
                pre_load_fwd_list.append(experiment_num + "_fwd.pickle")

        # Safety net for if evoked data gets here since saving doesn't work for it. 
        else:
            fwd = generate_fwd(plot_epoch)
            forward_genearted = True

    except:
        st.warning("""Error loading files from fwd cache (
            `simpl_eeg_capstone/src/pre_saved/epochs_info` and
            `simpl_eeg_capstone/src/pre_saved/epochs_info`). Cache will be cleared to
            avoid future errors.""")

        epoch_list_to_clear = get_list_of_files_cache(HEADER_EPOCH_PATH)
        fwd_list_to_clear = get_list_of_files_cache(HEADER_FWD_PATH)

        for f in epoch_list_to_clear:
            os.remove(HEADER_EPOCH_PATH+'/'+f)
        for f in fwd_list_to_clear:
            os.remove(HEADER_FWD_PATH+'/'+f)
        fwd = generate_fwd(plot_epoch)
        forward_genearted = True

    # If 4 or more files have been added to the cache delete the oldest
    for i in range(0, len(pre_load_epoch_list)-2):
        if len(pre_load_fwd_list) >= 3:
            remove_epoch_path = HEADER_EPOCH_PATH+'/{0}'
            full_path = [remove_epoch_path.format(x) for x in pre_load_epoch_list]
            oldest_epoch = min(full_path, key=os.path.getctime)

            remove_epoch_path = HEADER_FWD_PATH+'/{0}'
            full_path = [remove_epoch_path.format(x) for x in pre_load_fwd_list]
            oldest_fwd = min(full_path, key=os.path.getctime)

            os.remove(oldest_fwd)
            os.remove(oldest_epoch)
    
    return fwd, forward_genearted
    


def main():
    """
    Populate and display the streamlit user interface
    """

    st.header("Visualize your EEG data")
    st.markdown(
        """
        Select the figures you wish to see in the sidebar to the left
        and they will render in the dropdowns below.
        Settings for all figures such as
        the timeframe to plot and color scheme can be specified in the sidebar.
        Settings for individual figures can be specified
        in their respective dropdowns.
        For more information on this product please refer to documentation at
        <a href='https://ubc-mds.github.io/simpl_eeg_capstone/user_interface.html'
        target="_blank">this link</a>.
        """,
        unsafe_allow_html=True
    )

    st.sidebar.header("Global Settings")

    render_options = list(SECTION_NAMES.values())

    render_list = st.sidebar.multiselect(
        "Select figures to render",
        render_options,
        default=[
            render_options[0]
        ],
        help="""Select which figures you wish to have rendered in their
        respective dropdowns. Any selected views will begin to render
        automatically except for the 3D brain map which must
        be activated in its dropdown due to a slow render time.
        """
    )

    # List of file types supported for data file and events file
    file_types = ['.set', '.vhdr', '.edf', '.EDF', '.bdf',
                  '.gdf', '.cnt', '.mff', '.nxe', '.EEG', '.eeg']
    #Not working file types: '.mff'

    events_file_types = ['.mat']

    # List of montages that can be loaded/used
    MNE_MONTAGES = [
        'auto',
        'None',
        'easycap-M1', 'easycap-M10',
        'EGI_256',
        'GSN-HydroCel-128', 'GSN-HydroCel-129', 'GSN-HydroCel-256',
        'GSN-HydroCel-257', 'GSN-HydroCel-32', 'GSN-HydroCel-64_1.0',
        'GSN-HydroCel-65_1.0',
        'biosemi128', 'biosemi16', 'biosemi160', 'biosemi256',
        'biosemi32', 'biosemi64',
        'mgh60', 'mgh70',
        'standard_1005', 'standard_1020', 'standard_alphabetic',
        'standard_postfixed', 'standard_prefixed', 'standard_primed',
        'artinis-octamon', 'artinis-brite23'
    ]

    # Get a list of all the folders in data/ containing at least one supported file type
    experiment_list = []
    for name in os.listdir("data/"):
        curr_path = os.path.join("data", name)
        if os.path.isdir(curr_path):
            for fname in os.listdir(curr_path):
                for ftype in file_types:
                    if fname.endswith(ftype):
                        experiment_list.append(name)
    
    #remove duplicate folder names 
    experiment_list = list(set(experiment_list))

    if not experiment_list:
        raise FileNotFoundError(
            """
            Please move at least one experiment folder
            to the data folder to use this app.
            At a minimum the folder must contain a file of one of the following types
            {}
            """.format(file_types)
        )

    experiment_num = st.sidebar.selectbox(
        "Select experiment directory",
        experiment_list,
        help="""List of folders in the "simpl_eeg_capstone/data" direcotry which
        contain at least one supported primary EEG data file.
        For formats that use events times files they may be placed in
        the same folder to build epochs from.
        The selected experiment will have its data used to render the figures.
        The currently supported primary EEG data file types are {}
        and the currently supported events file types are {}.
        Note that for the formats where data is spread between multiple files
        that secondary files will be loaded automatically.
        """.format(file_types, events_file_types)
    )

    # Load a default raw EEG file to extract info from
    default_raw_EEG_obj = generate_eeg_raw(experiment_num)

    if default_raw_EEG_obj.raw != None:
        max_secs = default_raw_EEG_obj.raw.times[-1]
        el1, el2 = str(datetime.timedelta(seconds=max_secs)).split(".")
        exp_len = el1 + "." + el2[0:2]
        max_time = str(datetime.timedelta(seconds=max_secs)).split(".")[0]
        refresh_rate = default_raw_EEG_obj.raw.info.get('sfreq')

        if default_raw_EEG_obj.raw.get_montage() == None:
            default_montage = get_working_montage(experiment_num, MNE_MONTAGES, 'auto', True)
        else:
            default_montage = 'auto'
    # If a file can't be loaded use default values to prevent crashing
    else:
        max_secs = 0.0
        exp_len = "0:00:00.00"
        max_time = "0:00:00"
        refresh_rate = 0.0
        default_montage = None

    advanced_file_settings = st.sidebar.checkbox(
        "Advanced File Settings",
        help="""Check to show advanced file loading settings.
        Allows you to pick specific files to load data and events from as well as which
        montage to apply to the data.
        If your data is not loading correctly try changing these settings.
        If a setting cannot be adjusted given your current file type (i.e. events are
        loaded from the main data file) then the option will not show up.""",
        value=False
    )

    if advanced_file_settings:

        # Get list of files with the accepted file types
        data_file_list = files_with_specific_extension(experiment_num, file_types)
        data_file = st.sidebar.selectbox(
            "Select data file",
            data_file_list,
            index=0,
            help="""Select the primary file to load your EEG data from. The currently
            supported file types are: {}. Default tries to load an appropriate file
            but is not guaranteed to work in all contexts.
            Any secondary data files will be loaded automatically (i.e. '.fdt' files
            when using '.set' as primary) """.format(file_types)
        )
        
        # If events are automatically loaded then don't give option to select events file
        if default_raw_EEG_obj.events_source == "primary data file":
            events_file = 'auto'
        else:
            events_file_list = files_with_specific_extension(experiment_num, events_file_types)

            events_file = st.sidebar.selectbox(
                "Select event file",
                events_file_list,
                index=0,
                help="""Select the event file to load and build epochs from.
                The currently supported data types are: {}.
                Default tries to load an appropriate file in the experiment directory but
                is not guaranteed to work in all contexts.""".format(events_file_types)
            )

        # Make columns for montage selector
        col1_montage_list, col2_montage_list = st.sidebar.beta_columns((3, 1))

        # Make selectable box + text above
        col2_montage_list.text("Working\nOnly")
        compatible_montages = col2_montage_list.checkbox(
            "",
            help="""Check to test all standard montages with the currently loaded
            data and only list the compatible ones in the montage type selector.
            *NOTE* this can takes quite some time and should only be used if you're
            uncertain of which montage is comptabile with your data."""
        )

        # Get list of montages that work with data
        montage_options =[]
        if compatible_montages:
            montage_options = get_working_montage(experiment_num, MNE_MONTAGES, data_file, False)
            if default_raw_EEG_obj.montage_source == "primary data file":
                montage_options.insert(0,'None')
                montage_options.insert(0,'auto')
        else:
            montage_options = MNE_MONTAGES

        # Set default index to the default montage if one exists
        montage_default_index = 0
        if compatible_montages == False and default_montage != None:
            montage_default_index = MNE_MONTAGES.index(default_montage)

        montage = col1_montage_list.selectbox(
            "Select montage to load",
            montage_options,
            index=montage_default_index,
            help="""The standard montage to be applied to the data.
            If montage information already exists in your data selecting "auto" or "None"
            will allow you to use that information instead.
            If "only show compatible montages" only compatible montages will be shown.
            This is required to use any of the visualizations since it contains the
            "digitization points" (the locations of EEG nodes).
            A full list of all options available can be found here
            https://mne.tools/dev/generated/mne.channels.make_standard_montage.html.
            """
        )
        # Default to tested/working montage if 'auto' is selected.
        if montage == 'auto':
            montage=default_montage
        
        # set_refrences = st.sidebar.checkbox(
        #     "Manually set EEG reference chs",
        #     value=False,
        #     help="""Check to manually set EEG reference channels. If left unchecked the
        #     existing reference  channels in the data will be used."""
        # )

        # if set_refrences:

        #     default_ch_names = default_raw_EEG_obj.raw.ch_names

        #     reference_chanels = st.sidebar.multiselect(
        #         "Select EEG reference channels",
        #         default_ch_names,
        #         default=[
        #             default_ch_names[0]
        #         ],
        #         help="""Select which channels you would like to set as your EEG reference
        #         channels.
        #         """
        #     )


    else:
        # If advanced file settings aren't used then rely on these defaults
        data_file='auto'
        events_file='auto'
        montage=default_montage
        if montage != None and montage != 'auto':
            st.warning("""Montage {} was loaded by default since it was the first montage that
            worked with the data. If this is not correct then please specify a montage under
            'Advanced File Settings".
            """.format(default_montage))
        
    
    # Build EEG object with changed settings to test before building epoch
    raw_EEG_obj = generate_eeg_raw(
        experiment_num,
        file_name = data_file,
        events_file = events_file,
        montage = montage,
    )

    # Error catching for if data is not loaded properly
    if raw_EEG_obj.raw != None:
        n_chans = len(mne.pick_types(raw_EEG_obj.raw.info, meg=False, eeg=True))
    else:
        st.error("""Primary data could not be loaded with the current settings. Please adjust
        your files and file settings and try again""")
        n_chans = 0

    # Display file loading stats to user
    load_statusA_col1, load_statusA_col2, load_statusA_col3 = st.sidebar.beta_columns(
        (1, 1, 1)
    )
    load_statusA_col1.text("""Data File:\n{}""".format(raw_EEG_obj.file_source))
    load_statusA_col2.text("""Event File:\n{}""".format(raw_EEG_obj.events_source))
    load_statusA_col3.text("""Montage:\n{}""".format(raw_EEG_obj.montage_source))
    # Display stats about loaded information
    load_statusB_col1, load_statusB_col2, load_statusB_col3 = st.sidebar.beta_columns(
        (1, 1, 1)
    )
    load_statusB_col1.text("""Exp Length:\n{}""".format(exp_len))
    load_statusB_col2.text("""Sample Frq:\n{} Hz""".format(refresh_rate))
    load_statusB_col3.text("""EEG chs:\n{} ch.""".format(n_chans))

    # Error check raw eeg object before building epoch
    if bool(raw_EEG_obj.file_source) == False:
        st.error("""No EEG data was loaded. Please ensure a file with the appropriate filetype
        {} is placed within the selected experiment directory.""".format(file_types))
        epoch_num_channels=None
    else:
        epoch_num_channels= n_chans
    
    # Check if event loading failed
    if raw_EEG_obj.events_source == "bad file":
        st.warning("""Selected (or auto loaded) events file flagged for having over
        5000 events. This is probably not an events file and might cause errors so
        no events have been loaded.
        """.format(file_types))
        epoch_num_channels=None
    else:
        epoch_num_channels= n_chans

    # Check if montage loading failed
    if bool(raw_EEG_obj.montage_source) == False:
        st.error("""No montage could be loaded. Montage data contains information
        about the "digitization points" (the locations of EEG nodes), which are
        required for all visualizations. Please select an appropriate montage for your
        current EEG data option under 'Advanced File Settings'.""")

    # If events file has been successfully loaded make "epoch" timing an option
    if bool(raw_EEG_obj.events):
        event_times=generate_event_times_only(raw_EEG_obj.events)
        events_file_loaded=True
        timestamp_options=["Epoch", "Time"]
    else:
        events_file_loaded = False
        timestamp_options=["Time"]
        st.warning("""No events file could be loaded. If you wish to use one please
        place the appropriate file in the same directory as your data file. If
        errors persist specify the event file name in "Advanced File Settings".""")

    col1, col2 = st.sidebar.beta_columns((1, 1.35))
    time_select = col1.radio(
        "Timestamp type",
        options=timestamp_options,
        help="""Select "Epoch" to render figures based around the timestamps
        specified in the events file.
        Select "Time" to specify a custom timestamp to
        render the animation from. Only "Time" is available if no event file
        can be loaded. 
        """
    )

    if time_select == "Time":
        # If epoch too short set start time to 0
        if max_secs < 5.0:
            start_time_default = "0:00:00"
        else:
            start_time_default = "0:00:05"

        start_time = col2.text_input(
            "Custom event time",
            value=start_time_default,
            max_chars=7,
            help="""The timestamp to render the figures around.
            Must be entered in the format "H:MM:SS".
            The max time with the currently selected experiment is "{}".
            """.format(max_time)
        )

        # Check if the time is in the right format/within the experiment timeframe
        start_second, in_timeframe = calculate_timeframe(start_time, raw_EEG_obj.raw)
        if in_timeframe == "wrong_format":
            st.error(
                "Time is in wrong format please use H:MM:SS.\n\n"
                "Rendering below is made with previous settings."
            )
        if in_timeframe == "exceeds":
            st.error(
                "Input time exceeds max timestamp of "
                f"the current experiment ({max_time})."
            )
        if in_timeframe == "negative":
            st.error(
                """Specified event time cannot be less than 0:00:00"""
            )
        epoch_num = 0
    else:
        # These parameters are only used when specifying time
        start_second = None
        in_timeframe = "epoch"

        # Keep track of time for each epoch
        epoch_times = {}
        # Keep track of epoch times less than 5 seconds so "seconds before" doesn't proceed 0
        epochs_less_than_1sec = []

        # Add evoked option
        epoch_times['evoked'] = 'evoked'

        # Create dictionary of epoch times and their timestamps
        if events_file_loaded:
            for i in range(len(event_times)):
                secs = round(event_times[i]/refresh_rate, 2)
                isec, fsec = divmod(round(secs*100), 100)
                event_time_str = "{}.{:02.0f}".format(datetime.timedelta(seconds=isec), fsec)
                label = str(i) + " (" + event_time_str + ")"
                epoch_times[i] = label
                if secs < 1.0:
                    epochs_less_than_1sec.append(i)

        epoch_num = col2.selectbox(
            "Event",
            options = list(epoch_times.keys()),
            format_func=lambda key: epoch_times[key],
            index = 1,
            help="""The number epoch to use in all of the figures.
            Epochs are generated in sequence based
            on the order of events in the events file.
            NOTE: evoked data can't be used with the raw voltage or brain map plots."""
        )

    # Auto set tmin default to not break by deafault if experiment is too short
    tmin_max = 10.0
    tmin_default = 0.3
    if in_timeframe == "yes" or in_timeframe == "min":
        tmin_max = min(float(start_second), 10.0)
    if in_timeframe == "min":
        tmin_default = 0.0
    if in_timeframe == "epoch":
        if epoch_num in epochs_less_than_1sec:
            tmin_default = 0.0

    tmin = st.sidebar.number_input(
        "Seconds before event",
        value=tmin_default,
        min_value=0.0,
        max_value=tmin_max,
        help="""The number of seconds prior to the specified timestamp
        to start the figures from.
        Min = 0.0, max = {}
        (with current settings).
        """.format(tmin_max)
    )

    # Auto set tmin default to not break by deafault if experiment is too short
    tmax_max = 10.0
    tmax_value_default = 0.7
    if in_timeframe == "yes" or in_timeframe == "max":
        seconds_to_end = round(max_secs - start_second, 2) - 0.01
        if seconds_to_end < 10.0:
            tmax_max = seconds_to_end
        if seconds_to_end < 0.7:
            tmax_value_default = seconds_to_end

    if raw_EEG_obj.raw == None:
        tmax_value_default = 0.01
        tmax_max = 0.02
    elif tmax_max > max_secs:
        tmax_max = max_secs
        tmax_value_default = max_secs

    tmax = st.sidebar.number_input(
        "Seconds after event",
        value=tmax_value_default,
        min_value=0.01,
        max_value=tmax_max,
        help="""The number of seconds after to the specified timestamp to end the epoch at.
         Min = 0.01, max = {} (with current settings).
        """.format(tmax_max)
    )

    # Create epoch to be used in visualizations
    epoch_obj = generate_epoch(
        experiment_num,
        epoch_num,
        tmin=-tmin,
        tmax=tmax,
        start_second=start_second,
        file_name = data_file,
        events_file = events_file,
        montage = montage
    )

    col1_step, col2_step = st.sidebar.beta_columns((2, 1))
    frame_steps = col1_step.number_input(
        "Number of timesteps per frame",
        value=50,
        min_value=1,
        help="""The number of recordings in the data to skip between
        each rendered frame in the figures. For example, if an experiment is
        recorded at 2048 Hz (2048 recordings per second) then setting
        this value to 2 will show ever second recording in the data and
        1024 frames will be rendered for every second of data.
        A value of 1 will lead to every recorded value being rendered
        as a frame. "Num. frames to render" represents how many frames of
        animation will be rendered in each figure.
        Min = 1.
        """
    )

    # Store information about events/epoch so far
    events = epoch_obj.all_epochs.events
    epoch = epoch_obj.epoch
    plot_epoch = epoch_obj.skip_n_steps(frame_steps)
    plot_axis_limits = get_axis_lims(plot_epoch)
    fwd_generated = False

    if plot_epoch.times.shape[0] <= 2:
        st.warning("""WARNING: At least 3 frames must be rendered for
        the 3D brain plot to work due
        to neccesary pre-processing steps.""")

    col2_step.text(
        """-----------\nNum. frames\nto render:\n{}
        """.format(plot_epoch.times.shape[0])
    )

    col1, col2 = st.sidebar.beta_columns((2, 1))
    colormap = col1.selectbox(
        "Select color Scheme",
        ["RdBu_r", "PiYG", "PuOr", "BrBG", "Spectral", "turbo"],
        format_func=lambda name: name.capitalize(),
        help="""The color scheme to use on all of the figures."""
    )

    with col2:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        mat = np.arange(100).reshape((10, 10))
        ax.imshow(mat, cmap=colormap)
        fig.patch.set_alpha(0)
        plt.axis("off")
        st.pyplot(fig)

    show_code = st.sidebar.checkbox(
        "Show Code",
        value=False,
        help="Show the source code used to generate rendered figures"
    )
    
    show_help = st.sidebar.checkbox(
        "Show Documentation",
        value=False,
        help="Show full documentation for functions used to generate rendered figures"
    )


    # Create sections
    class Section:
        """
        A class to represent an expander section

        Attributes:
            section_name : str
                title of the section
            render : bool
                whether or not the plot within the section should be rendered
            expander : st.expander
                streamlit expander object for the section
            plot_col : st.beta_column
                the left column for the plot elements
            widget_col : st.beta_column
                the right column for the widgets related to the section

        Methods:
            on_render():
                Prints help and
                adds an export button to the bottom of section's widget column
            generate_file_name(file_type="html"):
                Generates an export file name and success message function
            html_export(self, html_plot):
                Generates a file name and export a given plot as html
        """
        def __init__(self, name, render=False, expand=False):
            """Set up the expander and columns"""
            self.section_name = SECTION_NAMES[name]
            self.render = self.section_name in render_list
            self.expander = st.beta_expander(
                self.section_name,
                expanded=self.render
            )
            with self.expander:
                self.plot_col, self.widget_col = st.beta_columns((3, 1))

        def on_render(self, code):
            
            if show_code:
                self.expander.code(code)
            if show_help:
                self.expander.help(eval(code.replace("simpl_eeg.","").split("(")[0]))
            
            return self.widget_col.button(
                "Export",
                key=self.section_name,
                help="Export to the `simpl_eeg/exports` folder"
            )

        def generate_file_name(self, file_type="html"):
            """
            Generate an export file name and success message function

            Parameters:
                file_type : str (optional)
                    File extension. Defaults to "html".

            Returns:
                tuple of str, function:
                    The generated file name and success message function
            """

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")

            try:
                # make exports folder
                os.makedirs("exports")
            except FileExistsError:
                # directory already exists
                pass

            folder = "exports"
            file_name = self.section_name.replace(" ", "_")+"_"+timestamp
            file_name = folder+"/"+file_name+"."+file_type

            def success_message():
                """Display message when file successfully saved"""

                message = self.expander.success(
                    "Your file was saved: "+file_name
                )
                time.sleep(2)
                message.empty()

            return file_name, success_message

        def html_export(self, html_plot):
            """
            Generate a file name and export a plot as html
            Prints success message to screen

            Parameters:
                html_plot : html
                    The plot to export
            """

            file_name, send_message = self.generate_file_name()
            html_file = open(file_name, "w")
            html_file.write(html_plot)
            html_file.close()
            send_message()

    # set up expander sections
    expander_raw = Section("raw", render=False)
    expander_2d_head = Section("2d_head")
    expander_3d_head = Section("3d_head")
    expander_3d_brain = Section("3d_brain")
    expander_connectivity = Section("connectivity")
    expander_connectivity_circle = Section("connectivity_circle")

    # WIDGETS
    with expander_raw.widget_col:
        st.title("")
        noise_select = st.checkbox(
            "Whiten with noise covarience",
            help="""Check to estimate noise covariance matrix
            from the currently loaded epoch."""
        )
        noise_cov = mne.compute_covariance(
            epoch,
            tmax=tmax,
        ) if noise_select else None

        auto_scale = st.checkbox(
            "Use automatic scaling",
            value=True,
            help="""Whether or not to use the automatic MNE scaling.
            Checking this causes the scaling
            factor to match the 99.5th percentile of a subset of the
            corresponding data."""
        )
        if auto_scale:
            scaling = "auto"
        else:
            scaling = st.slider(
                "Adjust scale",
                min_value=1,
                max_value=100,
                value=20,
            )
            if noise_select:
                scaling = scaling * 1e-1
            else:
                scaling = scaling * 1e-6
        set_dim = st.checkbox(
            "Set custom plot dimensions",
            value=False,
            help="Set a custom width and height for the plot"
        )
        if set_dim:
            raw_height = st.slider(
                "Height (inches)",
                min_value=5.0,
                max_value=10.0,
                value=5.0
            )
            raw_width = st.slider(
                "Width (inches)",
                min_value=5.0,
                max_value=10.0,
                value=7.0
            )
        else:
            raw_height = None
            raw_width = None

    min_voltage_message = "The minimum value (in μV) to show on the plot"
    max_voltage_message = "The maximum value (in μV) to show on the plot"

    with expander_2d_head.widget_col:
        vmin_2d_head = st.number_input(
            "Minimum voltage (μV)",
            value=-40.0,
            help=min_voltage_message
        )
        vmax_2d_head = st.number_input(
            "Maximum voltage (μV)",
            value=-vmin_2d_head,
            min_value=vmin_2d_head,
            help=max_voltage_message
        )
        mark_options = [
            "dot",
            "r+",
            "channel_name",
            "none"
        ]
        mark_selection_2d = st.selectbox(
            "Select mark",
            mark_options,
            index=0,
            help="The type of mark to show for each node on the topomap."
        )
        advanced_options_2d = st.checkbox(
            "Advanced Options",
            value=False,
            key="2dAO"
        )
        if advanced_options_2d:
            f_rate_2d_head = get_f_rate_widget("f_rate_2d_head")

            colorbar_2d_headmap = st.checkbox(
                "Include colorbar",
                value=True,
                key="cbar_2d"
            )
            timestamps_2d_headmap = st.checkbox(
                "Include timestamps",
                value=True,
                key="tstamp_2d"
            )
            contours_2d = st.number_input(
                "Number of contours",
                value=0,
                min_value=0,
                max_value=50,
                help="The number of contour lines to draw on the heatmap. Min = 0, max = 50."
            )
            extrapolate_options_2d = [
                "head",
                "local",
                "box",
            ]
            extrapolate_2d = st.selectbox(
                "Select extrapolation",
                extrapolate_options_2d,
                index=0,
                help="""HEAD- Extrapolate out to the edges of the clipping circle.
                LOCAL- Extrapolate only to nearby points (approximately to
                points closer than median inter-electrode distance).
                BOX- Extrapolate to four points placed to form a square
                encompassing all data points, where each
                side of the square is three times the range
                of the data in the respective dimension.
                """
            )
            can_use_sphere_param=check_if_sphere_works(plot_epoch, extrapolate_2d)
            if can_use_sphere_param:
                sphere_2d = st.number_input(
                    "Sphere size",
                    value=round(plot_axis_limits[0]*-0.95,4),
                    min_value=0.0,
                    format="%.4f",
                    help="""The sphere parameters to use for the cartoon head. 100 is
                    the reccomended value. Min = 80, max = 120."""
                )
            else:
                st.text("""Cannot adjust sphere with current\ndata and extrapolation setting""")
                sphere_2d=round(plot_axis_limits[0]*-0.95,4),
            heat_res_2d = st.number_input(
                "Heatmap resolution",
                value=100,
                min_value=1,
                max_value=1000,
                help="""The resolution of the topomap heatmap image. Does not effect the resolution
                of the entire image but rather the heatmap itself (n pixels along each side).
                Min = 1, max = 1000."""
            )
        else:
            f_rate_2d_head = 12
            colorbar_2d_headmap = True
            timestamps_2d_headmap = True
            contours_2d = 0
            sphere_2d = 100
            heat_res_2d = 100
            extrapolate_2d = "head"

    with expander_3d_head.widget_col:
        vmin_3d_head = st.number_input(
            "Minimum voltage (μV) ",
            value=-40.0,
            help=min_voltage_message
        )
        vmax_3d_head = st.number_input(
            "Maximum voltage (μV) ",
            value=40.0,
            min_value=vmin_3d_head,
            help=max_voltage_message
        )

    with expander_3d_brain.widget_col:
        vmin_3d_brain = st.number_input(
            "Minimum voltage (μV)",
            value=-2.0,
            help=min_voltage_message
        )
        vmax_3d_brain = st.number_input(
            "Maximum voltage (μV)",
            value=2.0,
            min_value=vmin_3d_brain,
            help=max_voltage_message
        )
        view_option_dict = {
            "lat": "Lateral",
            "dor": "Dorsal",
            "fro": "Frontal",
            "med": "Medial",
            "ros": "Rostral",
            "cau": "Caudal",
            "ven": "Ventral",
            "par": "Parietal",
        }
        view_selection = st.multiselect(
            "Select view(s)",
            options=list(view_option_dict.keys()),
            format_func=lambda key: view_option_dict[key],
            default=["lat"],
            help="""The viewing angle of the brain to render.
            Note that a different (slightly slower) figure
            rendering method is used whenever more than one view is
            selected OR if brain hemi is set to "both".
            """
        )
        hemi_options_dict = {
            "lh": "Left",
            "rh": "Right",
            "both": "Both"
        }
        hemi_selection = st.selectbox(
            "Select brain hemisphere",
            options=list(hemi_options_dict.keys()),
            format_func=lambda key: hemi_options_dict[key],
            help="""The side of the brain to render.
            If "both" is selected the right hemi of the brain will be rendered
            for the entire top row with the left hemi rendered in the bottom row.
            Note that a different (slower) figure
            rendering method is used whenever more than one view is selected
            OR if brain hemi is set to "both".
            """
        )
        spacing_value = st.selectbox(
            "Spacing type",
            ["oct4", "oct5", "oct6", "oct7", "ico3", "ico4", "ico5", "ico6"],
            index=1,
            help="""The spacing to use for the source space. "oct" uses a recursively
            subdivided octahedron and "ico" uses a recursively subdivided
            icosahedron. It is reccomended to use oct5 for speed and oct6 for
            detail. Increasing the number leads to an exponential increase in
            render time.
            """
        )
        advanced_options_brain = st.checkbox(
            "Advanced Options",
            value=False,
            key="brainAO"
        )
        if advanced_options_brain:
            f_rate_3d_brain = get_f_rate_widget("f_rate_3d_brain")
            colorbar_brain = st.checkbox(
                "Include colorbar",
                value=True,
                key="cbar_brain"
            )
            timestamps_brain = st.checkbox("Include timestamps", value=True, key = "tstamp_brain")

            smoothing_amount = st.number_input(
                "Number of smoothing steps",
                value=2,
                min_value=1,
                help="""The amount of smoothing to apply to the brain model."""
            )
            use_non_MNE_colors = st.checkbox(
                "Use non-MNE color palette",
                value=False,
                key="braincolor",
                help="""The default MNE color palette is reccomended
                for this figure as it includes texturing on the brain.
                Select this if you still wish to use the color palette
                specified in the sidebar.
                """
            )
        else:
            f_rate_3d_brain = DEFAULT_FRAME_RATE
            colorbar_brain = True
            timestamps_brain = True
            smoothing_amount = 2
            use_non_MNE_colors = False

    with expander_connectivity.widget_col:

        # Connection type and min/max value widgets
        connection_type, cmin, cmax = get_shared_conn_widgets(
            epoch,
            frame_steps,
            "conn"
        )

        # Node pair widgets
        node_pair_options = list(connectivity.PAIR_OPTIONS.keys())

        pair_selection = st.selectbox(
            "Select node pair template",
            node_pair_options,
            index=2,
            format_func=lambda name: name.replace("_", " ").capitalize(),
            help="""Select node pairs template to show only selected nodes.
            These can be further customized after selecting the template
            in the node pair textbox below. WARNING: This was built to work
            with a 19ch node layout only so selections may not be accurate
            for different layouts."""
        )

        selected_pairs = []
        if pair_selection == "all_pairs":
            selected_pairs = connectivity.PAIR_OPTIONS[pair_selection]
        else:
            custom_pair_selection = st.text_area(
                "Customize pairs to render",
                connectivity.PAIR_OPTIONS[pair_selection],
                help="""Enter comma separated pairs below in format
                Node1-Node2, Node3-Node4 to customize selection"""
            )
            selected_pairs = custom_pair_selection

        # Advanced options
        advanced_options_conn = st.checkbox(
            "Advanced Options",
            value=False,
            key="connAO"
        )

        if advanced_options_conn:
            f_rate_connectivity = get_f_rate_widget("f_rate_connectivity")

            # Line width widgets
            line_width_type = st.checkbox(
                "Set static line width",
                False,
                help="""Use static line width rather than dynamic line
                width based on connectivity score"""
            )

            conn_line_width = None
            if line_width_type is True:
                conn_line_width = st.slider(
                    "Select line width",
                    min_value=0.5,
                    max_value=5.5,
                    value=1.5,
                    help="Select a custom line width"
                )

            colorbar_conn = st.checkbox(
                "Include colorbar",
                value=True,
                key="conn_colorbar",
                help="Show colorbar on plot"
            )

            timestamps_conn = st.checkbox(
                "Include timestamps",
                value=True,
                key="conn_timestamps",
                help="Show timestamps on plot"
            )

            show_sphere_conn = st.checkbox(
                "Show sphere",
                value=True,
                key="conn_sphere",
                help="""Show sphere to represent head.
                If a montage was used to load the node locations then the
                head cannot be disabled."""
            )

            conn_sphere_coords = None
            readjust_conn_sphere = False

            if show_sphere_conn:
                
                adjust_sphere_conn = st.selectbox(
                    "Adjust sphere type",
                    ["Auto size, auto alignment",
                    "Auto size, no alignment",
                    "Auto size, with alignment",
                    "Manually specify values"],
                    index=0,
                    help="""Options for adjusting how the sphere will be scaled and aligned.
                    If sphere is mis-aligned try turning alignment on and off. If mis-alignment
                    persists then values can be manually specified.
                    """
                )

                if adjust_sphere_conn == "Auto size, auto alignment":
                    readjust_conn_sphere='auto'
                
                elif adjust_sphere_conn == "Auto size, no alignment":
                    readjust_conn_sphere=False
                
                elif adjust_sphere_conn == "Auto size, with alignment":
                    readjust_conn_sphere=True

                elif adjust_sphere_conn == "Manually specify values":
                    readjust_conn_sphere=False

                    if plot_axis_limits[0] <= -100:
                        manual_sphere_readjust_def=True
                    else:
                        manual_sphere_readjust_def=False

                    conn_sphere_x = st.number_input(
                        "Sphere X",
                        value=plot_axis_limits[0]*-0.0851 if manual_sphere_readjust_def else 0.0,
                        format="%.4f"
                    )
                    conn_sphere_y = st.number_input(
                        "Sphere Y",
                        value=plot_axis_limits[0]*0.142 if manual_sphere_readjust_def else 0.0,
                        format="%.4f"
                    )
                    conn_sphere_z = st.number_input(
                        "Sphere Z",
                        value=0.0,
                        format="%.4f"
                    )
                    conn_sphere_radius = st.number_input(
                        "Sphere radius",
                        value=plot_axis_limits[0]*-0.946,
                        min_value=0.0,
                        format="%.4f"
                    )
                    conn_sphere_coords = (conn_sphere_x, conn_sphere_y, conn_sphere_z, conn_sphere_radius)
                #else:
                    # conn_sphere_x=9
                    # conn_sphere_y=-15
                    # conn_sphere_z=0
                    # conn_sphere_radius=100
                    #conn_sphere_coords = None
                #conn_sphere_coords = (conn_sphere_x, conn_sphere_y, conn_sphere_z, conn_sphere_radius)
            # else:
            #     conn_sphere_coords = None

        else:
        # No advanced options specified for connectivity plot
            f_rate_connectivity = DEFAULT_FRAME_RATE
            conn_line_width = None
            colorbar_conn = True
            timestamps_conn = True
            show_sphere_conn = True
            readjust_conn_sphere='auto'
            conn_sphere_coords = None

    with expander_connectivity_circle.widget_col:

        # Connection type and min/max value widgets
        conn_type_circle, cmin_circle, cmax_circle = get_shared_conn_widgets(
            epoch,
            frame_steps,
            "circle"
        )

        # Maximum connections widget
        max_connections = st.number_input(
            "Maximum connections to display",
            min_value=0,
            max_value=n_chans*n_chans,
            value=n_chans+1,
            help="Select the maximum number of connection measurements to show"
        )

        

        # Advanced options
        advanced_options_circle = st.checkbox(
            "Advanced Options",
            value=False,
            key="circleAO"
        )

        if advanced_options_circle:
            f_rate_circle = get_f_rate_widget("f_rate_circle")

            # Line width widget
            conn_circle_line_width = st.slider(
                "Select line width ",
                min_value=1,
                max_value=5,
                value=2,
                help="Select a custom line width"
            )

            colorbar_circle = st.checkbox(
                "Include colorbar",
                value=True,
                key="circle_colorbar",
                help="Show colorbar on plot"
            )

            timestamps_circle = st.checkbox(
                "Include timestamps",
                value=True,
                key="circle_timestamps",
                help="Show timestamps on plot"
            )

        else:
            f_rate_circle = DEFAULT_FRAME_RATE
            conn_circle_line_width = 2
            colorbar_circle = True
            timestamps_circle = True


    # PLOTS
    def default_message(name):
        """Returns a message for non-rendered plots for a given section name"""

        return st.markdown(
            """
                \n
                Select your customizations,
                then add "%s" to the list of figures to render on the sidebar.
                \n
                **WARNING:depending on your settings,
                rendering may take a while...**
                \n
            """ % name
        )

    with expander_raw.plot_col:
        if expander_raw.render:

            if type(epoch) is not mne.evoked.EvokedArray:
                plot, code = render_raw_voltage_plot(
                    epoch,
                    remove_xlabel=True,
                    show_scrollbars=False,
                    height=raw_height,
                    width=raw_width,
                    events=np.array(events),
                    scalings=scaling,
                    noise_cov=noise_cov,
                    event_id=epoch.event_id
                )

                expander_raw.plot_col.pyplot(plot)

                export = expander_raw.on_render(code)
                if export:
                    file_name, send_message = expander_raw.generate_file_name(
                        "svg"
                    )
                    plot.savefig(file_name)
                    send_message()

            else:
                st.warning("""Voltage plot not available when using evoked data.""")

        else:
            default_message(expander_raw.section_name)

    with expander_2d_head.plot_col:
        if expander_2d_head.render:
            with st.spinner(SPINNER_MESSAGE):
                html_plot, code = animate_ui_2d_head(
                    plot_epoch,
                    colormap=colormap,
                    vmin=vmin_2d_head,
                    vmax=vmax_2d_head,
                    mark=mark_selection_2d,
                    colorbar=colorbar_2d_headmap,
                    timestamp=timestamps_2d_headmap,
                    extrapolate=extrapolate_2d,
                    contours=contours_2d,
                    sphere=sphere_2d,
                    res=heat_res_2d,
                    frame_rate = f_rate_2d_head
                )

                components.html(
                    html_plot,
                    height=600,
                    width=700
                )

            export = expander_2d_head.on_render(code)
            if export:
                expander_2d_head.html_export(html_plot)
        else:
            default_message(expander_2d_head.section_name)

    with expander_3d_head.plot_col:
        if expander_3d_head.render:
            with st.spinner(SPINNER_MESSAGE):
                plot, code = animate_ui_3d_head(
                    plot_epoch,
                    colormap=colormap,
                    vmin=vmin_3d_head,
                    vmax=vmax_3d_head
                )
                st.plotly_chart(
                    plot,
                    use_container_width=True
                )
                export = expander_3d_head.on_render(code)
                if export:
                    file_name, send_message = expander_3d_head.generate_file_name()
                    plot.write_html(file_name)
                    send_message()
        else:
            default_message(expander_3d_head.section_name)

    with expander_3d_brain.plot_col:
        if type(epoch) is not mne.evoked.EvokedArray:
            if expander_3d_brain.render:
                with st.spinner(SPINNER_MESSAGE):

                    st.markdown(
                        """
                        **WARNING:**
                        The 3D brain map animation takes a long time to compute.
                        Are you sure you want to generate this plot?
                        """
                    )
                    if st.checkbox("Yes I'm sure, bombs away!", value=False,
                    help =""" NOTE: This function uses a custom cache. The first time you load an
                    experiment it will need to generate a fwd and take a long time to render. This fwd
                    is then saved however making subsequent rendering of brain figures much faster. 
                    Your two most recent fwds will be saved in `simpl_eeg_capstone/src/pre_saved`.
                    """):

                        fwd_generated=False
                        fwd, fwd_generated = load_generate_fwd(
                            plot_epoch,
                            fwd_generated,
                            experiment_num,
                            HEADER_EPOCH_PATH,
                            HEADER_FWD_PATH
                        )


                        # # Loads an example epoch, checks if it's 'epoch.info' matches
                        # # if it does, loads an accompanying forward
                        # if fwd_generated is False:
                        #     with open(HEADER_EPOCH_PATH, "rb") as handle:
                        #         example_epoch = pickle.load(handle)
                        #     if plot_epoch.info.__dict__ == example_epoch.info.__dict__:
                        #         with open(HEADER_FWD_PATH, "rb") as handle:
                        #             fwd = pickle.load(handle)
                        #             if type(fwd) == mne.forward.forward.Forward:
                        #                 fwd_generated = True

                        # if fwd_generated is False:
                        #     fwd = generate_fwd(plot_epoch)
                        #     fwd_generated = True

                        stc = generate_stc(plot_epoch, fwd)

                        if use_non_MNE_colors is False:
                            colormap_brain = "mne"
                        else:
                            colormap_brain = colormap

                        html_plot, code = animate_ui_3d_brain(
                            stc=stc,
                            views=view_selection,
                            hemi=hemi_selection,
                            colormap=colormap_brain,
                            vmin=vmin_3d_brain,
                            vmax=vmax_3d_brain,
                            spacing=spacing_value,
                            smoothing_steps=smoothing_amount,
                            colorbar=colorbar_brain,
                            timestamp=timestamps_brain,
                            frame_rate=f_rate_3d_brain
                        )
                        components.html(
                            html_plot,
                            height=600,
                            width=600
                        )

                        export = expander_3d_brain.on_render(code)
                        if export:
                            expander_3d_brain.html_export(html_plot)
                    

            else:
                default_message(expander_3d_brain.section_name)
        else:
            st.warning("""Brain plot is not available when using evoked data.""")
            
    with expander_connectivity.plot_col:
        if expander_connectivity.render:
            with st.spinner(SPINNER_MESSAGE):
                html_plot, code = animate_ui_connectivity(
                    epoch,
                    calc_type=connection_type,
                    steps=frame_steps,
                    pair_list=selected_pairs,
                    colormap=colormap,
                    vmin=cmin,
                    vmax=cmax,
                    line_width=conn_line_width,
                    colorbar=colorbar_conn,
                    timestamp=timestamps_conn,
                    show_sphere=show_sphere_conn,
                    frame_rate=f_rate_connectivity,
                    sphere=conn_sphere_coords,
                    readjust_sphere=readjust_conn_sphere
                )
                components.html(
                    html_plot,
                    height=600,
                    width=600
                )

                export = expander_connectivity.on_render(code)
                if export:
                    expander_connectivity.html_export(html_plot)
        else:
            default_message(expander_connectivity.section_name)

    with expander_connectivity_circle.plot_col:
        if expander_connectivity_circle.render:
            html_plot, code = animate_ui_connectivity_circle(
                epoch,
                calc_type=conn_type_circle,
                steps=frame_steps,
                colormap=colormap,
                vmin=cmin_circle,
                vmax=cmax_circle,
                line_width=conn_circle_line_width,
                max_connections=max_connections,
                colorbar=colorbar_circle,
                timestamp=timestamps_circle,
                frame_rate=f_rate_circle
            )
            with st.spinner(SPINNER_MESSAGE):
                components.html(
                    html_plot,
                    height=600,
                    width=600
                )

            export = expander_connectivity_circle.on_render(code)
            if export:
                expander_connectivity_circle.html_export(html_plot)
        else:
            default_message(expander_connectivity_circle.section_name)


if __name__ == "__main__":
    main()
