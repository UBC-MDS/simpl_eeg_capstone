
import streamlit as st
import streamlit.components.v1 as components

import numpy as np
import mne
import scipy.io

import connectivity
# from mne.preprocessing import (create_eog_epochs, create_ecg_epochs,
#                                compute_proj_ecg, compute_proj_eog)

# from mne.viz import ClickableImage  # noqa
# from mne.viz import (plot_alignment, snapshot_brain_montage,
#                      set_3d_view)
# import matplotlib.animation as animation
# import pandas as pd
# import matplotlib
# import matplotlib.pyplot as plt


class eeg_file:

    def __init__(self, experiment):
        self.experiment = experiment
        self.mat = scipy.io.loadmat("data/"+experiment+"/impact locations.mat")
        self.raw = mne.io.read_raw_eeglab("data/"+experiment+"/fixica.set")

class epochs:

    # constructor
    def __init__(self, experiment):
        self.eeg_file = eeg_file(experiment)
        self.data = self.generate_epochs()

    def generate_epochs(self):
        stim_mock = self.eeg_file.mat["elecmax1"]

        events = ([[stim_mock[0][0], 0, 1]])
        for i in range(len(stim_mock[0])-1):
            events.append([stim_mock[0][i+1], 0, 1])
        events = np.array(events)

        epochs = mne.Epochs(self.eeg_file.raw, events, tmin=-0.3, tmax=0.7)
        event_dict = {"header": 1}

        epochs = mne.Epochs(self.eeg_file.raw, events, tmin=-0.3, tmax=0.7, event_id=event_dict,
                            preload=True)
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
    col1, col2 = st.beta_columns((2,1))

    st.sidebar.header("Visualize your EEG data based on the following options")
    experiment_num = st.sidebar.selectbox(
        "Select experiment",
        ["109", "97", "1112"]
    )
    time_select = st.sidebar.radio(
        "Time selection type",
        ["Time", "Epoch"]
    )

    st.sidebar.time_input("Start Time")
    st.sidebar.slider(
        "Duration (seconds)",
        min_value=0.5,
        max_value=10.0
    )

    epoch_obj = epochs(experiment_num)
    epoch = epoch_obj.data[0]

    col1.pyplot(
        epoch.plot()
    )

    with col2:
        anim = connectivity.animate_connectivity(epoch, "correlation")
        components.html(anim.to_jshtml(), height=600, width=600)

        anim = connectivity.animate_connectivity_circle(epoch, "correlation")
        components.html(anim.to_jshtml(), height=600, width=600)


if __name__ == "__main__":
    main()
