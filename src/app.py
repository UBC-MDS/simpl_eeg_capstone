
import streamlit as st
import streamlit.components.v1 as components

import numpy as np
import mne
import scipy.io

import raw_voltage
import connectivity
import topomap_2d
import topomap_3d_brain
import topomap_3d_head

import matplotlib.pyplot as plt

st.set_page_config(layout="wide")


class EEG_File:
    """
    A class to import and store relevant eeg files

    Attributes
    ----------
    experiment : str
        experiment folder name within the data folder
    mat : list(int)
        a list of integers representing impact times
    raw : mne.io.Raw
        raw experiment data in FIF format
    """

    def __init__(self, experiment):
        self.experiment = experiment
        self.mat = scipy.io.loadmat("data/"+experiment+"/impact locations.mat")
        self.raw = mne.io.read_raw_eeglab("data/"+experiment+"/fixica.set")


class Epochs:
    """
    A class to represent epochs and underlying data

    Attributes
    ----------
    eeg_file : EEG_File
        eeg file data
    data : mne.Epochs
        the generated epoch data

    Methods
    -------
    generate_epochs(duration, start_second):
        Calculates epochs based on a duration and start second
    generate_evoked():
        Converts epochs into evoked data
    """

    def __init__(self, experiment, duration=2, start_second=None):
        self.eeg_file = EEG_File(experiment)
        self.data = self.generate_epochs(duration, start_second)

    def generate_epochs(self, duration, start_second):
        if start_second:
            start_time = start_second*2049
            stim_mock = [[start_time]]
            tmin = 0
            tmax = duration
        else:
            stim_mock = self.eeg_file.mat["elecmax1"]
            tmin = -0.3
            tmax = tmin + duration
            print(tmax)

        events = [[i, 0, 1] for i in stim_mock[0]]
        event_dict = {"header": 1}

        epochs = mne.Epochs(
            self.eeg_file.raw,
            events,
            tmin=tmin,
            tmax=tmax,
            event_id=event_dict,
            preload=True,
            baseline=(0, 0)
        )

        return epochs

    def generate_evoked(self):
        evoked = self.data["header"].average()
        return evoked


def main():
    """
    Populate and display the streamlit user interface
    """

    st.sidebar.header("Visualize your EEG data based on the following options")
    experiment_num = st.sidebar.selectbox(
        "Select experiment",
        ["109", "97", "1112"]
    )
    time_select = st.sidebar.radio(
        "Time selection type",
        ["Time", "Epoch"]
    )
    if time_select == "Time":
        start_second = st.sidebar.selectbox(
            "Start second",
            [0, 100, 200, 300]
        )
        epoch_num = 0
        # st.sidebar.time_input("Start Time")
    else:
        start_second = None
        epoch_num = st.sidebar.selectbox(
            "Epoch",
            [i for i in range(33)]
        )

    duration = st.sidebar.slider(
        "Duration (seconds)",
        value=1.0,
        min_value=0.5,
        max_value=10.0
    )

    epoch_obj = Epochs(
        experiment_num,
        duration=duration,
        start_second=start_second
    )

    epoch = epoch_obj.data[epoch_num]

    with st.beta_expander("Raw Voltage Values", expanded=True):
        st.pyplot(
            raw_voltage.plot_voltage(epoch, {"events":epoch.events})
        )

    with st.beta_expander("3D Head Map", expanded=True):
        anim = topomap_3d_head.animate_3d_head(epoch)
        st.plotly_chart(anim)

    with st.beta_expander("2D Head Map", expanded=True):
        anim = topomap_2d.animate_topomap_2d(epoch, steps=100, frame_rate=1000)
        components.html(anim.to_jshtml(), height=600, width=600)

    with st.beta_expander("3D Brain Map", expanded=False):
        # brain = topomap_3d_brain.plot_topomap_3d_brain(epoch)
        brain = plt.figure()
        st.pyplot(brain)

    with st.beta_expander("Connectivity", expanded=True):
        col1, col2 = st.beta_columns((1, 1))

        with col1:
            pair_list = connectivity.PAIR_OPTIONS["far_coherence"]
            anim = connectivity.animate_connectivity(epoch, "correlation", pair_list=pair_list)
            components.html(anim.to_jshtml(), height=600, width=600)

        with col2:
            anim = connectivity.animate_connectivity_circle(epoch, "correlation")
            components.html(anim.to_jshtml(), height=600, width=600)


def test():
    epoch_obj = Epochs(
        "109",
        duration=1, 
        start_second=0
    )
    epoch = epoch_obj.data[0]
    brain = topomap_3d_brain.plot_topomap_3d_brain(epoch)   
    topomap_3d_brain.save_animated_topomap_3d_brain(brain, "test.gif")


if __name__ == "__main__":
    main()
