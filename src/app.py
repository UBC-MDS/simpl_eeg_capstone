
import streamlit as st
import streamlit.components.v1 as components

import numpy as np
import mne
import scipy.io

from eeg import (
    eeg_objects,
    raw_voltage,
    connectivity,
    topomap_2d,
    topomap_3d_brain,
    topomap_3d_head
)

import matplotlib.pyplot as plt

st.set_page_config(layout="wide")


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
            "Start second",
            value=0,
            min_value=0
        )
        epoch_num = 0
    else:
        start_second = None
        epoch_num = st.sidebar.selectbox(
            "Epoch",
            [i for i in range(33)]
        )

    duration = st.sidebar.number_input(
        "Duration (seconds)",
        value=1.0,
        min_value=0.5,
        max_value=15.0
    )

    colormap = st.sidebar.selectbox(
        "Select Colour Scheme",
        ["RdBu_r", "hot", "cool", "inferno", "turbo", "rainbow"]
    )

    epoch_obj = eeg_objects.Epochs(
        experiment_num,
        duration=duration,
        start_second=start_second
    )

    events = epoch_obj.data.events
    epoch = epoch_obj.get_nth_epoch(epoch_num)

    with st.beta_expander("Raw Voltage Values", expanded=True):
        kwargs = {
            "show_scrollbars": False
        }

        # show impact times if epochs selected
        if(time_select == "Epoch"):
            kwargs["events"] = np.array(events)
        st.pyplot(
            raw_voltage.plot_voltage(epoch, **kwargs)
        )

    with st.beta_expander("2D and 3D Head Map", expanded=True):
        col1, col2 = st.beta_columns((1, 1))

        with col1:
            steps = epoch.time_as_index(epoch.times[-1])[0]//frame_steps
            anim = topomap_2d.animate_topomap_2d(epoch, steps=steps, colormap=colormap)
            components.html(anim.to_jshtml(), height=600, width=600)
        with col2:
            anim = topomap_3d_head.animate_3d_head(epoch, steps=frame_steps, colormap=colormap)
            st.plotly_chart(anim, use_container_width=True)

    with st.beta_expander("3D Brain Map", expanded=False):
        # brain = topomap_3d_brain.plot_topomap_3d_brain(epoch)
        brain = plt.figure()
        st.pyplot(brain)

    with st.beta_expander("Connectivity", expanded=True):
        anim = connectivity.animate_all_conectivity(
            epoch,
            "correlation",
            show_every_nth_frame=frame_steps,
            colormap=colormap)
        components.html(anim.to_jshtml(), height=600)

        col1, col2 = st.beta_columns((1, 1))

        with col1:
            pair_list = connectivity.PAIR_OPTIONS["far_coherence"]
            anim = connectivity.animate_connectivity(epoch, "correlation", pair_list=pair_list,
                show_every_nth_frame=frame_steps, colormap=colormap)
            components.html(anim.to_jshtml(), height=600, width=600)

        with col2:
            anim = connectivity.animate_connectivity_circle(epoch, "correlation", 
                show_every_nth_frame=frame_steps, colormap=colormap)
            components.html(anim.to_jshtml(), height=600, width=600)


if __name__ == "__main__":
    main()
