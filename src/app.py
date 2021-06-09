
from os import PRIO_PGRP
import streamlit as st
import streamlit.components.v1 as components

import numpy as np
import mne
import scipy.io

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

SECTION_NAMES = {
    "raw": "Raw Voltage Values",
    "2d_head": "2D Head Map",
    "3d_head": "3D Head Map",
    "3d_brain": "3D Brain Map",
    "connectivity": "Connectivity",
    "connectivity_circle": "Connectivity Circle"
}

SPINNER_MESSAGE = "Rendering..."

st.set_page_config(layout="wide")

@st.cache(show_spinner=False)
def calculate_timeframe(start_time):
    if re.match('^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]$', start_time):
        start_time = start_time + ".00"
    elif re.match('^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]$', start_time) == False:
        if i == 0:
            # change to throw error
            print('start_time is in wrong format please use %H:%M:%S.%f or %H:%M:%S')
        elif i == 1:
            # change to throw error
            print('end_time is in wrong format please use %H:%M:%S.%f or %H:%M:%S')

    start = datetime.datetime.strptime(start_time, '%H:%M:%S.%f')
    zero = datetime.datetime.strptime('00:00:00.00', '%H:%M:%S.%f')
    
    return (start-zero).total_seconds()

@st.cache(show_spinner=False)
def animate_ui_3d_head(epoch, colormap, vmin, vmax):
    return topomap_3d_head.animate_3d_head(
        epoch,
        colormap=colormap,
        color_min=vmin,
        color_max=vmax
    )


@st.cache(show_spinner=False)
def animate_ui_2d_head(epoch, colormap, vmin, vmax, mark,
                       colorbar, timestamp, extrapolate, contours, sphere, res):
    anim = topomap_2d.animate_topomap_2d(
        epoch,
        colormap=colormap,
        cmin=vmin,
        cmax=vmax,
        mark=mark,
        colorbar=colorbar,
        timestamp=timestamp,
        extrapolate=extrapolate,
        contours=contours,
        sphere = sphere,
        res = res
    )
    return anim.to_jshtml()


@st.cache(show_spinner=False)
def animate_ui_3d_head(epoch, colormap, vmin, vmax):
    return topomap_3d_head.animate_3d_head(
        epoch,
        colormap=colormap,
        color_min=vmin,
        color_max=vmax
    )


@st.cache(show_spinner=False)
def generate_stc(epoch):
    fwd = topomap_3d_brain.create_fsaverage_forward(epoch)
    return (topomap_3d_brain.create_inverse_solution(epoch, fwd))


@st.cache(show_spinner=False)
def animate_ui_3d_brain(epoch, view_selection, stc, hemi, cmin, cmax):
    anim = topomap_3d_brain.animate_matplot_brain(epoch,
                                                  views=view_selection,
                                                  stc = stc,
                                                  hemi = hemi,
                                                  cmin = cmin,
                                                  cmax = cmax)
    return anim.to_jshtml()


@st.cache(show_spinner=False)
def animate_ui_connectivity(epoch, connection_type, steps, pair_list, colormap, vmin, vmax, line_width):
    anim = connectivity.animate_connectivity(
        epoch,
        connection_type,
        steps=steps,
        pair_list=pair_list,
        colormap=colormap,
        vmin=vmin,
        vmax=vmax,
        line_width=line_width,
    )
    return anim.to_jshtml()


@st.cache(show_spinner=False)
def animate_ui_connectivity_circle(epoch, connection_type, steps, colormap, vmin, vmax, line_width, max_connections):
    anim = connectivity.animate_connectivity_circle(
        epoch,
        connection_type,
        steps=steps,
        colormap=colormap,
        vmin=vmin,
        vmax=vmax,
        line_width=line_width,
        max_connections=max_connections
    )
    return anim.to_jshtml()

@st.cache(show_spinner=False)
def generate_epoch(experiment_num, tmin, tmax, start_second, epoch_num):
    epoch_obj = eeg_objects.Epochs(
        experiment_num,
        tmin=-tmin,
        tmax=tmax,
        start_second=start_second
    )
    epoch_obj.set_nth_epoch(epoch_num)
    return epoch_obj

def get_shared_conn_widgets(epoch, frame_steps, key):

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
        format_func=lambda name: name.replace("_", " ").capitalize()
    )
    default_cmin = -1.0
    default_cmax = 1.0
    if(connection_type == "envelope_correlation"):
        default_cmin = 0.0

    label = "Minimum Value"
    cmin = st.number_input(
        label,
        value=default_cmin,
        key=label+key
    )

    label = "Maximum Value"
    cmax = st.number_input(
        label,
        value=default_cmax,
        min_value=cmin,
        key=label+key
    )

    return connection_type, cmin, cmax


def main():
    """
    Populate and display the streamlit user interface
    """

    st.header("Visualize your EEG data")
    st.markdown("""
    Select the figures you wish to see in the sidebar to the left and they will render in the dropdowns below. 
    Settings that will be applied to each of the plots such as the timeframe to plot and color scheme can be specified in the sidebar.
    Individual settings for each of the plots can be changed in their respective dropdowns.
    """)

    st.sidebar.header("Global Settings")

    render_options = list(SECTION_NAMES.values())

    render_list = st.sidebar.multiselect(
        "Select figures to render",
        render_options,
        default=[
            render_options[0]
        ]
    )

    experiment_num = st.sidebar.selectbox(
        "Select experiment",
        [ name for name in os.listdir("data/") if os.path.isdir(os.path.join("data", name)) ]
    )


    frame_steps = st.sidebar.number_input(
        "Number of timesteps per frame",
        value=50,
        min_value=0
    )

    col1, col2 = st.sidebar.beta_columns((1, 1))
    time_select = col1.radio(
        "Time selection type",
        ["Epoch", "Time"]
    )
    if time_select == "Time":
        start_time = col2.text_input(
            "Custom impact time",
            value="00:00:05.00",
            max_chars=11
        )
        start_second = int(calculate_timeframe(start_time))
        epoch_num = 0
    else:
        start_second = None
        epoch_num = col2.selectbox(
            "Epoch",
            [i for i in range(33)]
        )

    tmin = st.sidebar.number_input(
        "Seconds before impact",
        value=0.3,
        min_value=0.01,
        max_value=min(float(start_second), 10.0) if start_second else 10.0
    )
    tmax = st.sidebar.number_input(
        "Seconds after impact",
        value=0.7,
        min_value=0.01,
        max_value=10.0
    )

    col1, col2 = st.sidebar.beta_columns((2, 1))
    colormap = col1.selectbox(
        "Select Colour Scheme",
        ["RdBu_r", "PiYG", "PuOr", "BrBG", "Spectral", "turbo"],
        format_func=lambda name: name.capitalize()
    )

    with col2:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        mat = np.arange(100).reshape((10, 10))
        ax.imshow(mat, cmap=colormap)
        fig.patch.set_alpha(0)
        plt.axis("off")
        st.pyplot(fig)

    # Create epoch
    epoch_obj = generate_epoch(
        experiment_num,
        tmin,
        tmax,
        start_second,
        epoch_num
    )

    stc_generated = False

    events = epoch_obj.data.events
    epoch = epoch_obj.epoch
    plot_epoch = epoch_obj.skip_n_steps(frame_steps)

    # Create sections
    class Section:
        def __init__(self, name, render=False, expand=False):
            self.section_name = SECTION_NAMES[name]
            self.render = self.section_name in render_list
            self.expander = st.beta_expander(
                self.section_name,
                expanded=self.render
            )
            with self.expander:
                self.plot_col, self.widget_col = st.beta_columns((3, 1))

    expander_raw = Section("raw", render=False)
    expander_2d_head = Section("2d_head")
    expander_3d_head = Section("3d_head")
    expander_3d_brain = Section("3d_brain")
    expander_connectivity = Section("connectivity")
    expander_connectivity_circle = Section("connectivity_circle")

    #### WIDGETS ####
    with expander_raw.widget_col:
        st.title("")
        noise_select = st.checkbox("Whiten with noise covarience")
        noise_cov = mne.compute_covariance(
            epoch,
            tmax=tmax
        ) if noise_select else None

        auto_scale = st.checkbox("Use automatic scaling", value=True)
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

    with expander_2d_head.widget_col:
        vmin_2d_head = st.number_input(
            "Minimum Voltage (uV)",
            value=-40.0
        )
        vmax_2d_head = st.number_input(
            "Maximum Voltage (uV)",
            value=40.0,
            min_value=vmin_2d_head
        )
        mark_options = [
            "dot",
            "r+",
            "channel_name",
            "none"
        ]
        mark_selection_2d = st.selectbox(
            "Select view",
            mark_options,
            index = 0
        )
        colorbar_2d_headmap = st.checkbox("Include colorbar", value=True)
        timestamps_2d_headmap = st.checkbox("Include timestamps", value=True)
        extrapolate_options_2d = [
            "head",
            "local",
            "box",
        ]
        extrapolate_2d = st.selectbox(
            "Select extrapolation",
            extrapolate_options_2d,
            index = 0
        )
        contours_2d = st.number_input(
            "Number of contours",
            value=0,
            min_value=0,
            max_value=50
        )
        sphere_2d = st.number_input(
            "Sphere size",
            value=100,
            min_value=80,
            max_value=120
        )
        heat_res_2d = st.number_input(
            "Heatmap resolution",
            value=100,
            min_value=1,
            max_value=1000
        )

    with expander_3d_head.widget_col:
        vmin_3d_head = st.number_input(
            "Minimum Voltage (uV) ",
            value=-40.0
        )
        vmax_3d_head = st.number_input(
            "Maximum Voltage (uV) ",
            value=40.0,
            min_value=vmin_3d_head
        )

    with expander_3d_brain.widget_col:
        view_option_dict = {
            "lat": "Lateral",
            "dor": "Dorsal",
            "fro": "Frontal",
            "med": "med__",
            "ros": "Ros__",
            "cau": "Cau__",
            "ven": "Ven__",
            "par": "Par__",
        }
        view_selection = st.multiselect(
            "Select view",
            options=list(view_option_dict.keys()),
            format_func=lambda key: view_option_dict[key],
            default=["lat"]
        )

        hemi_options_dict = {
            "lh": "Left",
            "rh": "Right",
            "both": "Both"
        }
        hemi_selection = st.selectbox(
            "Select brain hemi",
            options=list(hemi_options_dict.keys()),
            format_func=lambda key: hemi_options_dict[key],
        )

        vmin_3d_brain = st.number_input(
            "Minimum Voltage (uV)",
            value=-5.0
        )

        vmax_3d_brain = st.number_input(
            "Maximum Voltage (uV)",
            value=5.0,
            min_value=vmin_3d_brain
        )

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
            format_func=lambda name: name.replace("_", " ").capitalize()
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
            False
        )

        conn_line_width = None
        if line_width_type is True:
            conn_line_width = st.slider(
                "Select line width",
                min_value=1,
                max_value=5,
                value=2
            )

    with expander_connectivity_circle.widget_col:

        # Connection type and min/max value widgets
        connection_type, cmin, cmax = get_shared_conn_widgets(epoch, frame_steps, "circle")

        # Line width widget
        conn_circle_line_width = st.slider(
            "Select line width ",
            min_value=1,
            max_value=5,
            value=2
        )

        # Maximum connections widget
        max_connections = st.number_input(
            "Maximum connections to display",
            min_value=0,
            max_value=len(epoch.ch_names)*len(epoch.ch_names),
            value=20
        )

    #### PLOTS ####
    default_message = lambda name: st.markdown(
            """
                \n
                Select your customizations, 
                then add "%s" to the list of figures to render on the sidebar.
                \n
                **WARNING: depending on your settings, rendering may take a while...**
                \n
            """ % name
        )

    if expander_raw.render:
        plot = raw_voltage.plot_voltage(
                epoch,
                show_scrollbars=False,
                events=np.array(events),
                scalings=scaling,
                noise_cov=noise_cov,
                event_id=epoch.event_id,
        )
        expander_raw.plot_col.pyplot(plot)

        download = expander_raw.widget_col.button(
            "Export",
            key=expander_raw.section_name,
            help="Export svg to the `simpl_eeg/exports` folder"
        )
        if download:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
            folder = "exports"
            file_name = expander_raw.section_name.replace(" ", "_")+"_"+timestamp
            file_name = folder+"/"+file_name+".svg"
            plot.savefig(file_name)
            message = expander_raw.expander.success("Your file was saved: "+file_name)
            time.sleep(2)
            message.empty()
    else:
        default_message(expander_raw.section_name)

    with expander_2d_head.plot_col:
        if expander_2d_head.render:
            with st.spinner(SPINNER_MESSAGE):
                components.html(
                    animate_ui_2d_head(
                        plot_epoch,
                        colormap,
                        vmin_2d_head,
                        vmax_2d_head,
                        mark_selection_2d,
                        colorbar_2d_headmap,
                        timestamps_2d_headmap,
                        extrapolate_2d,
                        contours_2d,
                        sphere_2d,
                        heat_res_2d
                    ),
                    height=600,
                    width=700
                )
        else:
            default_message(expander_2d_head.section_name)

    with expander_3d_head.plot_col:
        if expander_3d_head.render:
            with st.spinner(SPINNER_MESSAGE):
                st.plotly_chart(
                    animate_ui_3d_head(
                        plot_epoch,
                        colormap,
                        vmin_3d_head,
                        vmax_3d_head
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
                    The first time you run will take longer than subsequent runs
                    (some preprocessing must occur).
                    NOTE: Selecting "lh" or "rh" and "both" is currently broken.
                    """
                )
                if st.button("Bombs away!"):

                    if stc_generated == False:
                        stc = generate_stc(plot_epoch)
                        stc_generated = True

                    components.html(
                        animate_ui_3d_brain(plot_epoch,
                                            view_selection,
                                            stc,
                                            hemi_selection,
                                            vmin_3d_brain,
                                            vmax_3d_brain),
                        height=600,
                        width=600
                    )
        else:
            default_message(expander_3d_brain.section_name)

    with expander_connectivity.plot_col:
        if expander_connectivity.render:
            with st.spinner(SPINNER_MESSAGE):
                components.html(
                    animate_ui_connectivity(
                        epoch,
                        connection_type,
                        frame_steps,
                        selected_pairs,
                        colormap,
                        cmin,
                        cmax,
                        conn_line_width
                    ),
                    height=600,
                    width=600
                )
        else:
            default_message(expander_connectivity.section_name)

    with expander_connectivity_circle.plot_col:
        if expander_connectivity_circle.render:
            with st.spinner(SPINNER_MESSAGE):
                components.html(
                    animate_ui_connectivity_circle(
                        epoch,
                        connection_type,
                        frame_steps,
                        colormap,
                        cmin,
                        cmax,
                        conn_circle_line_width,
                        max_connections
                    ),
                    height=600,
                    width=600
                )
        else:
            default_message(expander_connectivity_circle.section_name)


if __name__ == "__main__":
    main()

