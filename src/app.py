
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

st.set_page_config(layout="wide")


@st.cache(show_spinner=False)
def animate_2d_head(epoch, frame_steps, colormap, vmin, vmax):
    steps = epoch.time_as_index(epoch.times[-1])[0]//frame_steps
    anim = topomap_2d.animate_topomap_2d(
        epoch,
        steps=steps,
        colormap=colormap,
        color_lims=[vmin, vmax]
    )
    return anim.to_jshtml()


@st.cache(show_spinner=False)
def animate_3d_head(epoch, colormap, vmin, vmax):
    return topomap_3d_head.animate_3d_head(
        epoch,
        colormap=colormap,
        color_min=vmin,
        color_max=vmax
    )


@st.cache(show_spinner=False)
def animate_3d_brain(epoch,view_selection):
    anim = topomap_3d_brain.animate_matplot_brain(epoch, views=view_selection, background="w")
    return anim.to_jshtml()


@st.cache(show_spinner=False)
def animate_ui_connectivity(epoch, connection_type, steps, pair_list, colormap, cmin, cmax, line_width):
    anim = connectivity.animate_connectivity(
        epoch,
        connection_type,
        steps=steps,
        pair_list=pair_list,
        colormap=colormap,
        cmin=cmin,
        cmax=cmax,
        line_width=line_width
    )
    return anim.to_jshtml()


@st.cache(show_spinner=False)
def animate_ui_connectivity_circle(epoch, connection_type, steps, colormap, cmin, cmax, line_width):
    anim = connectivity.animate_connectivity_circle(
        epoch,
        connection_type,
        steps=steps,
        colormap=colormap,
        cmin=cmin,
        cmax=cmax,
        line_width=line_width
    )
    return anim.to_jshtml()


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

    with st.beta_expander("Raw Voltage Values", expanded=True):
        kwargs = {
            "show_scrollbars": False,
            "events": np.array(events)
        }

        st.pyplot(
            raw_voltage.plot_voltage(epoch, **kwargs)
        )

    with st.beta_expander("2D Head Map", expanded=True):
        col1, col2 = st.beta_columns((3, 1))

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
        with col1:
            components.html(
                animate_2d_head(plot_epoch, 1, colormap, vmin_2d_head, vmax_2d_head),
                height=600,
                width=700
            )

    with st.beta_expander("3D Head Map", expanded=True):
        col1, col2 = st.beta_columns((3, 1))

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
        with col1:
            st.plotly_chart(
                animate_3d_head(plot_epoch, colormap, vmin_3d_head, vmax_3d_head),
                use_container_width=True
            )

    with st.beta_expander("3D Brain Map", expanded=True):
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
        col1, col2 = st.beta_columns((3, 1))
        with col1:
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
        with col2:
            st.header("")
            show_brain = st.button("Run")

        if show_brain:
            with st.spinner("Rendering..."):
                components.html(
                    animate_3d_brain(plot_epoch, view_selection),
                    height=600,
                    width=600
                )

    with st.beta_expander("Connectivity", expanded=True):
        col1, col2 = st.beta_columns((3, 1))

        with col2:

            connectivity_methods = [
                "correlation",
                "spectral_connectivity",
                "envelope_correlation",
            ]
            if (len(epoch.times)//frame_steps) >= 100:
                connectivity_methods.append("covariance")

            connection_type = st.selectbox(
                "Select connection calculation",
                connectivity_methods
            )
            default_cmin = -1.0
            default_cmax = 1.0
            if(connection_type == "envelope_correlation"):
                default_cmin = 0.0

            cmin = st.number_input(
                "Minimum Value",
                value=default_cmin
            )
            cmax = st.number_input(
                "Maximum Value",
                value=default_cmax,
                min_value=cmin
            )

            line_width_type = st.checkbox(
                "Set line width",
                False
            )

            line_width = None
            if line_width_type is True:
                line_width = st.slider(
                    "Select line width",
                    min_value=1,
                    max_value=5,
                    value=2
                )

        with col1:

            components.html(
                animate_ui_connectivity_circle(
                    epoch,
                    connection_type,
                    frame_steps,
                    colormap,
                    cmin,
                    cmax,
                    line_width
                ),
                height=600,
                width=600
            )

        col1, col2 = st.beta_columns((3, 1))
        with col2:
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
                    "Enter comma separated pairs below in format Node1-Node2, Node3-Node4 to customize",
                    connectivity.PAIR_OPTIONS[pair_selection]
                )
                selected_pairs = custom_pair_selection

        with col1:
            components.html(
                animate_ui_connectivity(
                    epoch,
                    connection_type,
                    frame_steps,
                    selected_pairs,
                    colormap,
                    cmin,
                    cmax,
                    line_width
                ),
                height=600,
                width=600
            )

if __name__ == "__main__":
    main()
