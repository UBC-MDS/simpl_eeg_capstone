
import streamlit as st
import streamlit.components.v1 as components

import numpy as np
import mne
import scipy.io

import connectivity
import topomap_2d

st.set_page_config(layout="wide")

class eeg_file:

    def __init__(self, experiment):
        self.experiment = experiment
        self.mat = scipy.io.loadmat("data/"+experiment+"/impact locations.mat")
        self.raw = mne.io.read_raw_eeglab("data/"+experiment+"/fixica.set")


class epochs:

    def __init__(self, experiment, duration=2, start_second=None):
        self.eeg_file = eeg_file(experiment)
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
    # file_option = st.sidebar.radio('File upload', ["Selection","Upload"])
    # if file_option == "Selection":
    #     st.sidebar.selectbox('Select experiment', ["109","97","1112"])
    # else:
    #     #streamlit run your_script.py --server.maxUploadSize=1028
    #     st.sidebar.file_uploader('File uploader')
    col1, col2 = st.beta_columns((1, 1))

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

    epoch_obj = epochs(
        experiment_num,
        duration=duration,
        start_second=start_second
    )

    epoch = epoch_obj.data[epoch_num]

    st.pyplot(
        epoch.plot()
    )

    with col1:
        anim = connectivity.animate_connectivity(epoch, "correlation")
        components.html(anim.to_jshtml(), height=600, width=600)

    with col2:
        anim = connectivity.animate_connectivity_circle(epoch, "correlation")
        components.html(anim.to_jshtml(), height=600, width=600)

        # anim = topomap_2d.animate_topomap_2d(epoch, show_every_nth_frame=20)
        # components.html(anim.to_jshtml(), height=600, width=600)


if __name__ == "__main__":
    main()
 