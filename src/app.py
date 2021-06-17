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

DATA_FOLDER = "data/"
HEADER_EPOCH_PATH = "src/pre_saved/epochs/header_epoch.pickle"
HEADER_FWD_PATH = "src/pre_saved/forward/header_fwd.pickle"

st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
        .streamlit-expanderHeader{font-size:120%;}
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache(show_spinner=False)
def calculate_timeframe(start_time, raw):
    """Parse time from string and determine position in raw data

    Args:
        start_time (str): The start time in format H:M:S
        raw (mne.Raw): The full experiment data

    Returns:
        tuple(int, int): The time in seconds and the index
    """
    if re.match('^0{1,}:0{1,}:0{1,}$', start_time):
        return True, -1
    if re.match('^[0-9]{1,}:[0-9]{1,}:[0-9]{1,}$', start_time):
        start = datetime.datetime.strptime(start_time, '%H:%M:%S')
        zero = datetime.datetime.strptime('0:00:00', '%H:%M:%S')
        seconds = (start-zero).total_seconds()
        if seconds >= raw.times[-1]:
            in_timeframe = 0
        else:
            in_timeframe = 1
        return int(seconds), in_timeframe
    else:
        return None, 1


@st.cache(show_spinner=False)
def generate_stc_epoch(epoch):
    """Helper function for 3D brain map
    generate inverse solution from forward"""
    fwd = topomap_3d_brain.create_fsaverage_forward(epoch)
    return (topomap_3d_brain.create_inverse_solution(epoch, fwd))


@st.cache(show_spinner=False)
def generate_stc_fwd(epoch, fwd):
    """Helper function for 3D brain map - Generate forward solution"""
    return (topomap_3d_brain.create_inverse_solution(epoch, fwd))


@st.cache(show_spinner=False)
def animate_ui_2d_head(epoch, **kwargs):
    """Caching wrapper function to call topomap_2d.animate_topomap_2d"""
    anim = topomap_2d.animate_topomap_2d(epoch, **kwargs)
    return anim.to_jshtml()


@st.cache(show_spinner=False)
def animate_ui_3d_head(epoch, **kwargs):
    """Caching wrapper function to call topomap_3d_head.animate_3d_head"""
    return topomap_3d_head.animate_3d_head(epoch, **kwargs)


@st.cache(show_spinner=False)
def animate_ui_3d_brain(epoch, **kwargs):
    """Caching wrapper function to call
    topomap_3d_brain.animate_matplot_brain"""
    anim = topomap_3d_brain.animate_matplot_brain(epoch, **kwargs)
    return anim.to_jshtml()


@st.cache(show_spinner=False)
def animate_ui_connectivity(epoch, connection_type, **kwargs):
    """Caching wrapper function to call connectivity.animate_connectivity"""
    anim = connectivity.animate_connectivity(
        epoch,
        connection_type,
        **kwargs
    )
    return anim.to_jshtml()


@st.cache(show_spinner=False)
def animate_ui_connectivity_circle(epoch, connection_type, **kwargs):
    """Caching wrapper function to call
    connectivity.animate_connectivity_circle"""
    anim = connectivity.animate_connectivity_circle(
        epoch,
        connection_type,
        **kwargs
    )
    return anim.to_jshtml()


@st.cache(show_spinner=False)
def generate_eeg_file(experiment_num):
    """Helper function for creating standalone eeg_file object"""
    gen_eeg_file = eeg_objects.EEG_File(
        DATA_FOLDER+experiment_num
    )
    return gen_eeg_file


@st.cache(show_spinner=False)
def generate_epoch(experiment_num, tmin, tmax, start_second, epoch_num):
    """Generate a custom epoch

    Args:
        experiment_num (str):
            Folder name of experiment
        tmin (float):
            Seconds before the event time
        tmax (float):
            Seconds after the event time
        start_second (int):
            The second of event
        epoch_num (int, optional):
            An epoch of interest to store.

    Returns:
        eeg_objects.Epoch: The generated epoch object
    """

    epoch_obj = eeg_objects.Epochs(
        DATA_FOLDER+experiment_num,
        tmin=-tmin,
        tmax=tmax,
        start_second=start_second
    )
    epoch_obj.set_nth_epoch(epoch_num)
    return epoch_obj


def get_shared_conn_widgets(epoch, frame_steps, key):
    """Helper function for producing shared widgets for
    connectivity sections"""

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


def main():
    """
    Populate and display the streamlit user interface
    """

    st.header("Visualize your EEG data")
    st.markdown(
        """
        Select the figures you wish to see in the sidebar to the left
        and they will render in the dropdowns below.
        Settings that will be applied to each of the figures such as
        the timeframe to plot and color scheme can be specified in the sidebar.
        Individual settings for each of the figures can be changed
        in their respective dropdowns.
        """
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

    col1_exp, col2_exp = st.sidebar.beta_columns((2, 1))
    experiment_num = col1_exp.selectbox(
        "Select experiment",
        [name for name in os.listdir("data/") if os.path.isdir(os.path.join("data", name))],
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
    max_time = str(datetime.timedelta(seconds=max_secs-1)).split(".")[0]

    col2_exp.text(
        """----------\nExperiment\nlength:\n{}""".format(exp_len)
    )

    col1, col2 = st.sidebar.beta_columns((1, 1.3))
    time_select = col1.radio(
        "Timestamp type",
        ["Epoch", "Time"],
        help="""Select "Epoch" to render figures based around the timestamps
        specified in the "impact locations.mat".
        Select "Time" to specify a custom timestamp to
        render the animation from.
        """
    )

    if time_select == "Time":
        start_time = col2.text_input(
            "Custom event time",
            value="0:00:05",
            max_chars=7,
            help="""The timestamp to render the figures around.
            Must be entered in the format "H:MM:SS".
            The max time with the currently selected experiment is "{}"
            (one second before the total length
            of the experiment).""".format(max_time)
        )
        start_second, in_timeframe = calculate_timeframe(start_time, raw_epoch_obj.raw)
        if start_second == None:
            st.error('Time is in wrong format please use H:MM:SS')
        if in_timeframe == 0:
            st.error(
                "Input time exceeds max timestamp of "
                f"the current experiment ({max_time})."
            )
        if in_timeframe == -1:
            st.error(
                """Specified event time cannot be 0:00:00.
                If you wish to see the experiment from the earliest time
                possible then please specify an event time of
                00:00:01 and a "Seconds before event"
                value of 1.0"""
            )
        epoch_num = 0
    else:
        start_second = None

        refresh_rate = raw_epoch_obj.raw.info.get('sfreq')
        event_times = raw_epoch_obj.mat['elecmax1'][0]
        epoch_times = {}

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

    tmin = st.sidebar.number_input(
        "Seconds before event",
        value=0.3,
        min_value=0.01,
        max_value=min(float(start_second), 10.0) if start_second else 10.0,
        help="""The number of seconds prior to the specified timestamp
        to start the figures from.
        Min = 0.01, max = 10
        (also cannot be a value that will cause the
        timestamp to go beyond 00:00:00).
        """
    )

    tmax_max_value = 10.0
    if start_second != None:
        seconds_to_end = round(max_secs - start_second,2) - 0.01
        if seconds_to_end < 10.0:
            tmax_max_value = seconds_to_end

    tmax = st.sidebar.number_input(
        "Seconds after event",
        value=0.7,
        min_value=0.01,
        max_value=tmax_max_value,
        help="""The number of seconds after to the specified timestamp to end the epoch at.
        Cannot be a value that will cause
        the timestamp to go beyond the max time. Min = 0.01, max = {}
        (with current settings).
        """.format(tmax_max_value)
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

    events = epoch_obj.data.events
    epoch = epoch_obj.epoch
    plot_epoch = epoch_obj.skip_n_steps(frame_steps)

    stc_generated = False

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
        "Select Colour Scheme",
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

    # Create sections
    class Section:
        """
        A class to represent an expander section

        Attributes
        ----------
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

        Methods
        -------
        export_button():
            Adds an export button to the bottom of section's widget column
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

        def export_button(self):
            """Add an export button to the bottom of widget column"""
            return self.widget_col.button(
                "Export",
                key=self.section_name,
                help="Export to the `simpl_eeg/exports` folder"
            )

        def generate_file_name(self, file_type="html"):
            """Generate an export file name and success message function

            Args:
                file_type (str, optional):
                    File extension. Defaults to "html".

            Returns:
                tuple(str, function):
                    The generated file name and success message function
            """

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
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

            Args:
                html_plot (html): The plot to export
            """

            file_name, send_message = self.generate_file_name()
            Html_file = open(file_name, "w")
            Html_file.write(html_plot)
            Html_file.close()
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
            help = """Whether or not to use the automatic MNE scaling.
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

    min_voltage_message = "The minimum value (in μV) to show on the plot"
    max_voltage_message = "The maximum value (in μV) to show on the plot"

    with expander_2d_head.widget_col:
        vmin_2d_head = st.number_input(
            "Minimum Voltage (μV)",
            value=-40.0,
            help = min_voltage_message
        )
        vmax_2d_head = st.number_input(
            "Maximum Voltage (μV)",
            value=40.0,
            min_value=vmin_2d_head,
            help = max_voltage_message
        )

        # Doesn't currently work for whatever reason.
        # Can't compare two number inputs.
        if vmax_2d_head < vmin_2d_head:
            st.error(
                "ERROR: Minimum Voltage Set higher than Maximum Voltage."
                "Please enter a valid input"
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
            help="The type of mark to show for each electrode on the topomap"
        )
        advanced_options_2d = st.checkbox(
            "Advanced Options",
            value=False,
            key="2dAO"
        )
        if advanced_options_2d:
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
                help="The number of contour lines to draw. Min = 0, max = 50."
            )
            sphere_2d = st.number_input(
                "Sphere size",
                value=100,
                min_value=80,
                max_value=120,
                help="""The sphere parameters to use for the cartoon head.
                Min = 80, max = 120."""
            )
            heat_res_2d = st.number_input(
                "Heatmap resolution",
                value=100,
                min_value=1,
                max_value=1000,
                help="""The resolution of the topomap image (n pixels along each side).
                Min = 0, max = 1000."""
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
            colorbar_2d_headmap = True
            timestamps_2d_headmap = True
            contours_2d = 0
            sphere_2d = 100
            heat_res_2d = 100
            extrapolate_2d = "head"

    with expander_3d_head.widget_col:
        vmin_3d_head = st.number_input(
            "Minimum Voltage (μV) ",
            value=-40.0,
            help=min_voltage_message
        )
        vmax_3d_head = st.number_input(
            "Maximum Voltage (μV) ",
            value=40.0,
            min_value=vmin_3d_head,
            help=max_voltage_message
        )

    with expander_3d_brain.widget_col:
        vmin_3d_brain = st.number_input(
            "Minimum Voltage (μV)",
            value=-5.0,
            help=min_voltage_message
        )
        vmax_3d_brain = st.number_input(
            "Maximum Voltage (μV)",
            value=5.0,
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
            help="""
            The side of the brain to render.
            If "both" is selected the right hemi of the brain will be rendered
            for the entire top row with the left hemi rendered in the bottom row.
            Note that a different (slightly slower) figure
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
            icosahedron.Reccomend using oct5 for speed and oct6 for more
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
            use_non_MNE_colours = st.checkbox(
                "Use non-MNE colour palette",
                value=False,
                key="braincolour",
                help="""The default MNE color palette is reccomended
                for this figure as it includes texturing on the brain.
                Select this if you still wish to use the color palette
                specified in the sidebar.
                """
            )
        else:
            colorbar_brain = True
            timestamps_brain = True
            spacing_value = "oct5"
            smoothing_amount = 2
            use_non_MNE_colours = False

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
            index=1,
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
                """
                Enter comma separated pairs below in format
                Node1-Node2, Node3-Node4 to customize
                """,
                connectivity.PAIR_OPTIONS[pair_selection]
            )
            selected_pairs = custom_pair_selection

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
                max_value=5.0,
                value=1.5,
                help="Select a custom line width"
            )

    with expander_connectivity_circle.widget_col:

        # Connection type and min/max value widgets
        conn_type_circle, cmin_circle, cmax_circle = get_shared_conn_widgets(
            epoch,
            frame_steps,
            "circle"
        )

        # Line width widget
        conn_circle_line_width = st.slider(
            "Select line width ",
            min_value=1,
            max_value=5,
            value=2,
            help="Select a custom line width"
        )

        # Maximum connections widget
        max_connections = st.number_input(
            "Maximum connections to display",
            min_value=0,
            max_value=len(epoch.ch_names)*len(epoch.ch_names),
            value=20,
            help="Select the maximum number of connection measurements to show"
        )

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
            plot = raw_voltage.plot_voltage(
                epoch,
                remove_xlabel=True,
                show_scrollbars=False,
                events=np.array(events),
                scalings=scaling,
                noise_cov=noise_cov,
                event_id=epoch.event_id,
            )
            expander_raw.plot_col.pyplot(plot)

            export = expander_raw.export_button()
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
                html_plot = animate_ui_2d_head(
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
                    res=heat_res_2d
                )
                components.html(
                    html_plot,
                    height=600,
                    width=700
                )

            export = expander_2d_head.export_button()
            if export:
                expander_2d_head.html_export(html_plot)
        else:
            default_message(expander_2d_head.section_name)

    with expander_3d_head.plot_col:
        if expander_3d_head.render:
            with st.spinner(SPINNER_MESSAGE):
                st.plotly_chart(
                    animate_ui_3d_head(
                        plot_epoch,
                        colormap=colormap,
                        color_min=vmin_3d_head,
                        color_max=vmax_3d_head
                    ),
                    use_container_width=True
                )
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

                    # Loads an example epoch, checks if it matches conditions
                    # if it does, loads an accompanying forward
                    if stc_generated is False:
                        with open(HEADER_EPOCH_PATH, "rb") as handle:
                            example_epoch = pickle.load(handle)
                        if plot_epoch.info.__dict__ == example_epoch.info.__dict__:
                            with open(HEADER_FWD_PATH, "rb") as handle:
                                fwd = pickle.load(handle)
                                if type(fwd) == mne.forward.forward.Forward:
                                    stc = generate_stc_fwd(plot_epoch, fwd)
                                    stc_generated = True

                    if stc_generated is False:
                        stc = generate_stc_epoch(plot_epoch)
                        stc_generated = True
                    if use_non_MNE_colours is False:
                        colormap_brain = "mne"
                    else:
                        colormap_brain = colormap

                    html_plot = animate_ui_3d_brain(
                        epoch=plot_epoch,
                        views=view_selection,
                        stc=stc,
                        hemi=hemi_selection,
                        colormap=colormap_brain,
                        cmin=vmin_3d_brain,
                        cmax=vmax_3d_brain,
                        spacing=spacing_value,
                        smoothing_steps=smoothing_amount,
                        colorbar=colorbar_brain,
                        timestamp=timestamps_brain
                    )
                    components.html(
                        html_plot,
                        height=600,
                        width=600
                    )
                    export = expander_3d_brain.export_button()
                    if export:
                        expander_3d_brain.html_export(html_plot)
        else:
            default_message(expander_3d_brain.section_name)

    with expander_connectivity.plot_col:
        if expander_connectivity.render:
            with st.spinner(SPINNER_MESSAGE):
                html_plot = animate_ui_connectivity(
                    epoch,
                    connection_type,
                    steps=frame_steps,
                    pair_list=selected_pairs,
                    colormap=colormap,
                    vmin=cmin,
                    vmax=cmax,
                    line_width=conn_line_width
                )
                components.html(
                    html_plot,
                    height=600,
                    width=600
                )
                export = expander_connectivity.export_button()
                if export:
                    expander_connectivity.html_export(html_plot)
        else:
            default_message(expander_connectivity.section_name)

    with expander_connectivity_circle.plot_col:
        if expander_connectivity_circle.render:
            html_plot = animate_ui_connectivity_circle(
                epoch,
                conn_type_circle,
                steps=frame_steps,
                colormap=colormap,
                vmin=cmin_circle,
                vmax=cmax_circle,
                line_width=conn_circle_line_width,
                max_connections=max_connections
            )
            with st.spinner(SPINNER_MESSAGE):
                components.html(
                    html_plot,
                    height=600,
                    width=600
                )
            export = expander_connectivity_circle.export_button()
            if export:
                expander_connectivity_circle.html_export(html_plot)
        else:
            default_message(expander_connectivity_circle.section_name)


if __name__ == "__main__":
    main()
