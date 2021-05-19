
import streamlit as st
import numpy as np
import mne
import scipy.io
# from mne.preprocessing import (create_eog_epochs, create_ecg_epochs,
#                                compute_proj_ecg, compute_proj_eog)

# from mne.viz import ClickableImage  # noqa
# from mne.viz import (plot_alignment, snapshot_brain_montage,
#                      set_3d_view)
# import streamlit.components.v1 as components
# import matplotlib.animation as animation
# import pandas as pd
# import matplotlib
# import matplotlib.pyplot as plt


def get_epochs(raw, mat):
    stim_mock = mat["elecmax1"]

    events = ([[stim_mock[0][0], 0, 1]])
    for i in range(len(stim_mock[0])-1):
        events.append([stim_mock[0][i+1], 0, 1])
    events = np.array(events)

    epochs = mne.Epochs(raw, events, tmin=-0.3, tmax=0.7)
    event_dict = {"header": 1}

    epochs = mne.Epochs(raw, events, tmin=-0.3, tmax=0.7, event_id=event_dict,
                        preload=True)
    return epochs


def get_source_files(experiment):
    mat = scipy.io.loadmat("data/"+experiment+"/impact locations.mat")
    raw = mne.io.read_raw_eeglab("data/"+experiment+"/fixica.set")
    files = {
        "raw": raw,
        "mat": mat,
        "epochs": get_epochs(raw, mat)
    }
    return files


def generate_evoked(raw):
    epochs = get_epochs(raw)
    evoked = epochs["header"].average()
    return evoked


def main():
    # file_option = st.sidebar.radio('File upload', ["Selection","Upload"])
    # if file_option == "Selection":
    #     st.sidebar.selectbox('Select experiment', ["109","97","1112"])
    # else:
    #     #streamlit run your_script.py --server.maxUploadSize=1028
    #     st.sidebar.file_uploader('File uploader')

    col1, col2 = st.beta_columns(2)
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

    file_dict = get_source_files(experiment_num)

    col1.pyplot(
        file_dict["raw"].plot()
    )


if __name__ == "__main__":
    main()
