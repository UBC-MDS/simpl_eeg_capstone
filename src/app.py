import streamlit as st
import streamlit.components.v1 as components

import numpy as np
import mne

import os

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
HEADER_EPOCH_PATH = "src/pre_saved/epochs/header_epoch.pickle"
HEADER_FWD_PATH = "src/pre_saved/forward/header_fwd.pickle"

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
            The time in seconds and the index
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
def generate_eeg_file(experiment_num):
    """
    Helper function for creating standalone eeg_file object
    """
    gen_eeg_file = eeg_objects.EEG_File(
        DATA_FOLDER+experiment_num
    )
    return gen_eeg_file

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
def generate_epoch(experiment_num, tmin, tmax, start_second, epoch_num):
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

    epoch_obj = eeg_objects.Epochs(
        DATA_FOLDER+experiment_num,
        tmin=-tmin,
        tmax=tmax,
        start_second=start_second
    )
    epoch_obj.get_epoch(epoch_num)
    return epoch_obj


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

    experiment_list = []
    for name in os.listdir("data/"):
        curr_path = os.path.join("data", name)
        if os.path.isdir(curr_path):
            for fname in os.listdir(curr_path):
                if fname.endswith('.set'):
                    experiment_list.append(name)

    if not experiment_list:
        raise FileNotFoundError(
            """
            Please move at least one experiment folder
            to the data folder to use this app.
            At a minimum the folder must contain a .set file.
            """
        )

    col1_exp, col2_exp = st.sidebar.beta_columns((2, 1))
    experiment_num = col1_exp.selectbox(
        "Select experiment",
        experiment_list,
        help="""List of folders contained in the "data" folder.
        Each folder should represent one experiment and contain files labelled
        "fixica.fdt", "fixica.set", and "impact locations.mat".
        The selected experiment will have its data used to render the figures.
        """
    )

    raw_epoch_obj = generate_eeg_file(
        experiment_num
    )
    max_secs = raw_epoch_obj.raw.times[-1]
    el1, el2 = str(datetime.timedelta(seconds=max_secs)).split(".")
    exp_len = el1 + "." + el2[0:2]
    max_time = str(datetime.timedelta(seconds=max_secs)).split(".")[0]

    col2_exp.text(
        """----------\nExperiment\nlength:\n{}""".format(exp_len)
    )


    if bool(raw_epoch_obj.events):
        event_times=generate_event_times_only(raw_epoch_obj.events)
        event_file_loaded=True
        timestamp_options=["Epoch", "Time"]
    else:
        event_file_loaded = False
        timestamp_options=["Time"]
        st.warning("""No events file could be loaded. If you wish to use one and are
        using a .set file please label it 'impact locations.mat' and place it in the
        same folder as the .set file.""")

    col1, col2 = st.sidebar.beta_columns((1, 1.35))
    time_select = col1.radio(
        "Timestamp type",
        options=timestamp_options,
        help="""Select "Epoch" to render figures based around the timestamps
        specified in the "impact locations.mat".
        Select "Time" to specify a custom timestamp to
        render the animation from. Only "Time" is available if no event file
        can be loaded. 
        """
    )

    if time_select == "Time":
        start_time = col2.text_input(
            "Custom event time",
            value="0:00:05",
            max_chars=7,
            help="""The timestamp to render the figures around.
            Must be entered in the format "H:MM:SS".
            The max time with the currently selected experiment is "{}".
            """.format(max_time)
        )
        start_second, in_timeframe = calculate_timeframe(start_time, raw_epoch_obj.raw)
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
        start_second = None
        in_timeframe = "epoch"

        refresh_rate = raw_epoch_obj.raw.info.get('sfreq')
        







        # #event_times = scipy.io.loadmat(DATA_FOLDER+'/'+experiment_num+'/'+'impact locations.mat')
        # import scipy.io
        # event_times = scipy.io.loadmat(DATA_FOLDER+'/'+experiment_num+'/'+'impact locations.mat')['elecmax1'][0]
        


        # if raw_epoch_obj.file_source == ".set" and bool(raw_epoch_obj.events):
        #     event_times = raw_epoch_obj.events["elecmax1"][0]
        #     event_file_loaded = True
        # elif raw_epoch_obj.file_source == ".set" and bool(raw_epoch_obj.events):
        #     event_times = raw_epoch_obj.events
        #     event_file_loaded = True







        epoch_times = {}

        if event_file_loaded:
            for i in range(len(event_times)):
                secs = round(event_times[i]/refresh_rate, 2)
                isec, fsec = divmod(round(secs*100), 100)
                event_time_str = "{}.{:02.0f}".format(datetime.timedelta(seconds=isec), fsec)
                label = str(i) + " (" + event_time_str + ")"
                epoch_times[i] = label


        epoch_num = col2.selectbox(
            "Event",
            options = list(epoch_times.keys()),
            format_func=lambda key: epoch_times[key],
            help="""The number epoch to use in all of the figures.
            Epochs are generated in sequence based
            on the order of events in the "event locations.mat" file.
            """
        )

    tmin_max = 10.0
    tmin_default = 0.3
    if in_timeframe == "yes" or in_timeframe == "min":
        tmin_max = min(float(start_second), 10.0)
    if in_timeframe == "min":
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

    tmax_max = 10.0
    tmax_value_default = 0.7
    if in_timeframe == "yes" or in_timeframe == "max":
        seconds_to_end = round(max_secs - start_second, 2) - 0.01
        if seconds_to_end < 10.0:
            tmax_max = seconds_to_end
        if seconds_to_end < 0.7:
            tmax_value_default = seconds_to_end

    tmax = st.sidebar.number_input(
        "Seconds after event",
        value=tmax_value_default,
        min_value=0.01,
        max_value=tmax_max,
        help="""The number of seconds after to the specified timestamp to end the epoch at.
         Min = 0.01, max = {} (with current settings).
        """.format(tmax_max)
    )

    # Create epoch
    epoch_obj = generate_epoch(
        experiment_num,
        tmin,
        tmax,
        start_second,
        epoch_num
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

    events = epoch_obj.all_epochs.events
    epoch = epoch_obj.epoch
    plot_epoch = epoch_obj.skip_n_steps(frame_steps)

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

    with col2:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        mat = np.arange(100).reshape((10, 10))
        ax.imshow(mat, cmap=colormap)
        fig.patch.set_alpha(0)
        plt.axis("off")
        st.pyplot(fig)

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
            value=40.0,
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
            sphere_2d = st.number_input(
                "Sphere size",
                value=100,
                min_value=80,
                max_value=120,
                help="""The sphere parameters to use for the cartoon head. 100 is
                the reccomended value. Min = 80, max = 120."""
            )
            heat_res_2d = st.number_input(
                "Heatmap resolution",
                value=100,
                min_value=1,
                max_value=1000,
                help="""The resolution of the topomap heatmap image. Does not effect the resolution
                of the entire image but rather the heatmap itself (n pixels along each side).
                Min = 1, max = 1000."""
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
            spacing_value = "oct5"
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
            in the node pair textbox below"""
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
                help="Show sphere to represent head"
            )

            if show_sphere_conn:
                adjust_spehre_conn = st.checkbox(
                    "Adjust sphere",
                    value=False,
                    key="connSp",
                    help="""Select to manually adjust the X/Y/Z coordinates and radius of the skull spehere if the
                    node locations are misplaced.
                    """
                )
                if adjust_spehre_conn:
                    conn_sphere_x = st.number_input(
                        "Sphere X",
                        value=9
                    )
                    conn_sphere_y = st.number_input(
                        "Sphere Y",
                        value=-15
                    )
                    conn_sphere_z = st.number_input(
                        "Sphere Z",
                        value=0
                    )
                    conn_sphere_radius = st.number_input(
                        "Sphere radius",
                        value=100
                    )
                else:
                    conn_sphere_x=9
                    conn_sphere_y=-15
                    conn_sphere_z=0
                    conn_sphere_radius=100
                conn_sphere_coords = (conn_sphere_x, conn_sphere_y, conn_sphere_z, conn_sphere_radius)
            else:
                conn_sphere_coords = None

        else:
            f_rate_connectivity = DEFAULT_FRAME_RATE
            conn_line_width = None
            colorbar_conn = True
            timestamps_conn = True
            show_sphere_conn = True
            if show_sphere_conn:
                conn_sphere_coords = (9, -15, 0, 100)
            else:
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
            max_value=len(epoch.ch_names)*len(epoch.ch_names),
            value=20,
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
            default_message(expander_raw.section_name)

    with expander_2d_head.plot_col:
        if expander_2d_head.render:
            with st.spinner(SPINNER_MESSAGE):
                html_plot, code = animate_ui_2d_head(
                    plot_epoch,
                    colormap=colormap,
                    cmin=vmin_2d_head,
                    cmax=vmax_2d_head,
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
                    color_min=vmin_3d_head,
                    color_max=vmax_3d_head
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
        if expander_3d_brain.render:
            with st.spinner(SPINNER_MESSAGE):
                st.markdown(
                    """
                    **WARNING:**
                    The 3D brain map animation takes a long time to compute.
                    Are you sure you want to generate this plot?
                    """
                )
                if st.checkbox("Yes I'm sure, bombs away!", value=False):

                    # Loads an example epoch, checks if it's 'epoch.info' matches
                    # if it does, loads an accompanying forward
                    if fwd_generated is False:
                        with open(HEADER_EPOCH_PATH, "rb") as handle:
                            example_epoch = pickle.load(handle)
                        if plot_epoch.info.__dict__ == example_epoch.info.__dict__:
                            with open(HEADER_FWD_PATH, "rb") as handle:
                                fwd = pickle.load(handle)
                                if type(fwd) == mne.forward.forward.Forward:
                                    fwd_generated = True

                    if fwd_generated is False:
                        fwd = generate_fwd(plot_epoch)
                        fwd_generated = True
                    
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
                        cmin=vmin_3d_brain,
                        cmax=vmax_3d_brain,
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
                    sphere=conn_sphere_coords
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
