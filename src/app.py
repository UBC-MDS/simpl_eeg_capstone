
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
def animate_2d_head(epoch, frame_steps, colormap):
    steps = epoch.time_as_index(epoch.times[-1])[0]//frame_steps
    anim = topomap_2d.animate_topomap_2d(epoch, steps=steps, colormap=colormap)
    return anim.to_jshtml()


@st.cache(show_spinner=False)
def animate_3d_head(epoch, colormap):
    return topomap_3d_head.animate_3d_head(epoch, colormap=colormap)


@st.cache(show_spinner=False)
def animate_3d_brain(epoch):
    #topomap_3d_brain.plot_topomap_3d_brain(epoch)
    return plt.figure()


@st.cache(show_spinner=False)
def animate_connectivity(epoch, colormap, frame_steps, pair_selection, connection_type):
    pair_list = connectivity.PAIR_OPTIONS[pair_selection]
    anim = connectivity.animate_connectivity(epoch, connection_type, pair_list=pair_list,
        show_every_nth_frame=frame_steps, colormap=colormap)
    return anim.to_jshtml()


@st.cache(show_spinner=False)
def animate_connectivity_circle(epoch, colormap, connection_type):
    anim = connectivity.animate_connectivity_circle(epoch, connection_type, colormap=colormap)
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
        max_value=10.0
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

    events = epoch_obj.data.events
    epoch = epoch_obj.get_nth_epoch(epoch_num)
    plot_epoch = epoch.copy().decimate(frame_steps)

    with st.beta_expander("Raw Voltage Values", expanded=True):
        kwargs = {
            "show_scrollbars": False,
            "events": np.array(events)
        }

        st.pyplot(
            raw_voltage.plot_voltage(epoch, **kwargs)
        )

    with st.beta_expander("2D Head Map", expanded=True):
        components.html(
            animate_2d_head(plot_epoch, 1, colormap),
            height=600,
            width=600
        )

    with st.beta_expander("3D Head Map", expanded=True):
        st.plotly_chart(
            animate_3d_head(plot_epoch, colormap),
            use_container_width=True
        )

    with st.beta_expander("3D Brain Map", expanded=False):
        st.pyplot(
            animate_3d_brain(plot_epoch)
        )

    with st.beta_expander("Connectivity", expanded=True):
        col1, col2 = st.beta_columns((3, 1))

        with col2:
            pair_selection = st.selectbox(
                "Pairs",
                list(connectivity.PAIR_OPTIONS.keys()),
                index=2
            )

            connection_type = st.selectbox(
                "Selection connection calculation",
                [
                    "correlation",
                    "covariance",
                    "spectral_connectivity",
                    "envelope_correlation",
                ]
            )

        with col1:
            components.html(
                animate_connectivity2(epoch, connection_type, steps=frame_steps, pair_list=pair_selection, colormap=colormap),
                height=600,
                width=600
            )

            components.html(
                animate_connectivity_circle(epoch, connection_type, steps=frame_steps, colormap=colormap),
                height=600,
                width=600
            )

if __name__ == "__main__":
    main()
