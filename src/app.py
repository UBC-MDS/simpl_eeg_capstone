
from os import PRIO_PGRP
import streamlit as st
import streamlit.components.v1 as components

import numpy as np
import mne
import scipy.io

from simpl_eeg import (
    eeg_objects,
    raw_voltage,
    connectivity,
    topomap_2d,
    topomap_3d_brain,
    topomap_3d_head
)

import matplotlib.pyplot as plt

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
def animate_ui_2d_head(epoch, colormap, vmin, vmax):
    anim = topomap_2d.animate_topomap_2d(
        epoch,
        colormap=colormap,
        cmin=vmin,
        cmax=vmax
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
def animate_ui_3d_brain(epoch, view_selection):
    anim = topomap_3d_brain.animate_matplot_brain(epoch, views=view_selection)
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
        key=label+key
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

    st.sidebar.header("Visualize your EEG data based on the following options")
    experiment_num = st.sidebar.selectbox(
        "Select experiment",
        ["109", "927", "1122"]
    )

    frame_steps = st.sidebar.number_input(
        "Number of timesteps per frame",
        value=50,
        min_value=0
    )

    time_select = st.sidebar.radio(
        "Time selection type",
        ["Epoch", "Time"]
    )
    if time_select == "Time":
        start_second = st.sidebar.number_input(
            "Custom impact second",
            value=1,
            min_value=1
        )
        epoch_num = 0
    else:
        start_second = None
        epoch_num = st.sidebar.selectbox(
            "Epoch",
            [i for i in range(33)]
        )

    tmin = st.sidebar.number_input(
        "Seconds before impact",
        value=0.3,
        min_value=0.0,
        max_value=min(float(start_second), 10.0) if start_second else 10.0
    )
    tmax = st.sidebar.number_input(
        "Seconds after impact",
        value=0.7,
        min_value=0.5,
        max_value=10.0
    )

    colormap = st.sidebar.selectbox(
        "Select Colour Scheme",
        ["RdBu_r", "hot", "cool", "inferno", "turbo", "rainbow"]
    )

    # Create epoch
    epoch_obj = eeg_objects.Epochs(
        experiment_num,
        tmin=-tmin,
        tmax=tmax,
        start_second=start_second
    )
    epoch_obj.set_nth_epoch(epoch_num)

    events = epoch_obj.data.events
    epoch = epoch_obj.epoch
    plot_epoch = epoch_obj.skip_n_steps(frame_steps)

    # Create sections
    # render_options = list(SECTION_NAMES.values())

    # render_list = st.multiselect(
    #     "Select figures to render",
    #     render_options,
    #     default=[
    #         render_options[0]
    #     ]
    # )

    class Section:
        def __init__(self, name, render=False, expand=False):
            self.section_name = SECTION_NAMES[name]
            self.render = render
            self.expander = st.beta_expander(self.section_name, expanded=expand)
            with self.expander:
                self.col1, self.col2 = st.beta_columns((3, 1))

        def get_columns(self):
            return self.col1, self.col2

        def run_button(self):
            with self.col1:
                self.render = st.button("Render", key=self.section_name)

    expander_raw = Section("raw", render=True)
    expander_2d_head = Section("2d_head")
    expander_3d_head = Section("3d_head")
    expander_3d_brain = Section("3d_brain")
    expander_connectivity = Section("connectivity")
    expander_connectivity_circle = Section("connectivity_circle")

    with expander_raw.expander:
        if expander_raw.render:
            st.pyplot(
                raw_voltage.plot_voltage(
                    epoch,
                    show_scrollbars=False,
                    events=np.array(events)
                )
            )

    with expander_2d_head.expander:
        col1, col2 = expander_2d_head.get_columns()

        with col2:
            vmin_2d_head = st.number_input(
                "Minimum Voltage (uV)",
                value=-40.0
            )
            vmax_2d_head = st.number_input(
                "Maximum Voltage (uV)",
                value=40.0,
                min_value=vmin_2d_head
            )
            expander_2d_head.run_button()

        with col1:
            if expander_2d_head.render:
                with st.spinner(SPINNER_MESSAGE):
                    components.html(
                        animate_ui_2d_head(
                            plot_epoch,
                            colormap,
                            vmin_2d_head,
                            vmax_2d_head
                        ),
                        height=600,
                        width=700
                    )

    with expander_3d_head.expander:
        col1, col2 = expander_3d_head.get_columns()

        with col2:
            vmin_3d_head = st.number_input(
                "Minimum Voltage (uV) ",
                value=-40.0
            )
            vmax_3d_head = st.number_input(
                "Maximum Voltage (uV) ",
                value=40.0,
                min_value=vmin_3d_head
            )
            expander_3d_head.run_button()

        with col1:
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

    with expander_3d_brain.expander:

        col1, col2 = expander_3d_brain.get_columns()
        with col2:
            view_options = [
                "lat",
                "dor",
                "fro"
            ]
            view_selection = st.multiselect(
                "Select view",
                view_options,
                default=["lat"]
            )
            st.markdown(
                """
                \n
                Select your customizations, 
                then click the *Run* button below to render the 3D brain map.
                \n
                **WARNING: rendering may take a while...**
                \n
                """
            )
            expander_3d_brain.run_button()

        with col1:
            if expander_3d_brain.render:
                with st.spinner(SPINNER_MESSAGE):
                    components.html(
                        animate_ui_3d_brain(plot_epoch, view_selection),
                        height=600,
                        width=600
                    )

    with expander_connectivity.expander:
        col1, col2 = expander_connectivity.get_columns()
        with col2:

            # Connection type and min/max value widgets
            connection_type, cmin, cmax = get_shared_conn_widgets(epoch, frame_steps, "conn")

            # Node pair widgets
            node_pair_options = list(connectivity.PAIR_OPTIONS.keys())

            pair_selection = st.selectbox(
                "Select node pair template",
                node_pair_options,
                index=1
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
            expander_connectivity.run_button()

        with col1:
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

    with expander_connectivity_circle.expander:

        col1, col2 = expander_connectivity_circle.get_columns()

        with col2:

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
            expander_connectivity_circle.run_button()

        with col1:
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


if __name__ == "__main__":
    main()
