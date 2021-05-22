"""Module for generating and animating the topographic map in a 3D head shape
"""

# import libraries
import mne
import numpy as np
import pandas as pd
import scipy.io
from scipy.interpolate import NearestNDInterpolator
import plotly
import plotly.graph_objects as go



def frame_args(duration):
    return {
        "frame": {"duration": duration},
        "mode": "immediate",
        "fromcurrent": True,
        "transition": {"duration": duration, "easing": "linear", "redraw": False},
    }

def get_standard_coord():
    """Generate an array of cartesian coordinates of the standard node locations ("standard_1005")

    Returns:
        array: A numpy array of cartesian coordinates of the standard node locations ("standard_1005")
    """
    montage = mne.channels.make_standard_montage("standard_1005")
    standard_coord_list = []
    for key, value in montage.get_positions()["ch_pos"].items():
        standard_coord_list.append(value.tolist())
    standard_coord_array = np.array(standard_coord_list)
    return montage, standard_coord_array

def interpolated_time(x, y, z, t):
    """The function to animate the 3D plot

    Args:
        x (array): A numpy array of X coordinates of all nodes for interpolation
        y (array): A numpy array of Y coordinates of all nodes for interpolation
        z (array): A numpy array of Z coordinates of all nodes for interpolation
        t (int): The time stampe we want to interpolate EEG voltages for

    Returns:
        array: A numpy array of interpolated EEG voltages
    """
    now = df[df["time"] == t]
    eeg = now.iloc[:, channels].mean().values
    interpolate_model = NearestNDInterpolator(node_coord, eeg)
    return interpolate_model(np.array(list(zip(x, y, z))))

def get_eeg_node(raw, standard_montage_list):
    """Get the electrode location from the raw data

    Args:
        raw (dataframe): The raw dataframe
        standard_montage_list (array): The numpy array which contains the cartesian coordinate of standard node location

    Returns:
        array: The electrode location from the raw data
    """
    node_list = []
    for channel in raw.get_montage().ch_names:
        node_list.append(standard_montage_list.get_positions()["ch_pos"][channel].tolist())
    node_coord = np.array(node_list)
    return node_coord

def get_node_dataframe(raw, montage):
    """Get the electrode name and electrode location from the raw data and save it in a dataframe

    Args:
        raw (dataframe): The raw dataframe
        montage (array): The numpy array which contains the cartesian coordinate of standard node location

    Returns:
        dataframe: A dataframe which contains the electrode name and electrode location from the raw data
    """
    node_list_name = []
    for channel in raw.get_montage().ch_names:
        node_list_name.append(
            [
                channel,
                montage.get_positions()["ch_pos"][channel][0],
                montage.get_positions()["ch_pos"][channel][1],
                montage.get_positions()["ch_pos"][channel][2],
            ]
    )
    node_df = pd.DataFrame(node_list_name, columns=["channel", "X", "Y", "Z"])
    return node_df

def animate_3d_head(raw, starting=0, ending=50, duration=10):
    """Plot an animated topographic map in a 3D head shape

    Args:
        raw (str): A file path for the EEGLab data  
        starting (int, optional): The starting time stamp of the animation. Defaults to 0.
        ending (int, optional): The ending time stamp of the animation. Defaults to 50.
        duration (int, optional): The duration of the animation, it could not be longer than the length of the data frame. Defaults to 10.
    """
    raw_data = mne.io.read_raw_eeglab(raw)
    raw_df = raw_data.to_data_frame()
    channel_names = raw_data.ch_names
    df =raw_df[(raw_df["time"] > starting) & (raw_df["time"] < ending)]
    standard_montage, standard_coord = get_standard_coord()
    x = np.array(standard_coord)[:, 0]
    y = np.array(standard_coord)[:, 1]
    z = np.array(standard_coord)[:, 2]
    node_coord = get_eeg_node(raw_data, standard_montage)
    nb_frames = duration
    node_df = get_node_dataframe(raw_data, standard_montage)
    fig = go.Figure(
    frames=[
        go.Frame(
            data=go.Mesh3d(
                x=np.array(standard_coord)[:, 0],
                y=np.array(standard_coord)[:, 1],
                z=np.array(standard_coord)[:, 2],
                colorscale="Bluered",
                colorbar_title="EEG Voltage",
                intensity=interpolated_time(x, y, z, k),
                intensitymode="vertex",
                alphahull=1,
                opacity=1,
            ),
            name=str(
                k
            ),  # you need to name the frame for the animation to behave properly
        )
        for k in nb_frames
    ]
)

    # Add data to be displayed before animation starts
    fig.add_trace(
        go.Mesh3d(
            x=np.array(standard_coord)[:, 0],
            y=np.array(standard_coord)[:, 1],
            z=np.array(standard_coord)[:, 2],
            colorscale="Bluered",
            colorbar_title="EEG Voltage",
            intensity=interpolated_time(x, y, z, 0),
            intensitymode="vertex",
            alphahull=1,
            opacity=1,
        )
    )
    fig.add_scatter3d(
        connectgaps=True,
        x=node_df["X"],
        y=node_df["Y"],
        z=node_df["Z"],
        text=node_df["channel"],
        mode="markers+text",
        marker={"size": 5, "color": "black"},
        textposition="top left",
        textfont=dict(family="sans serif", size=18, color="White"),
    )


    sliders = [
        {
            "pad": {"b": 10, "t": 60},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "steps": [
                {
                    "args": [[f.name], frame_args(0)],
                    "label": str(k),
                    "method": "animate",
                }
                for k, f in enumerate(fig.frames)
            ],
        }
    ]


    fig.update_layout(
        title="EEG Interpolated 3D Graph",
        width=1000,
        height=600,
        scene=dict(
            zaxis=dict(
                range=[
                    np.nan_to_num(np.array(standard_coord)[:, 2].tolist()).min(),
                    np.nan_to_num(np.array(standard_coord)[:, 2].tolist()).max(),
                ],
                autorange=False,
            ),
            aspectratio=dict(x=1.5, y=1.5, z=1),
        ),
        updatemenus=[
            {
                "buttons": [
                    {
                        "args": [None, frame_args(0)],
                        "label": "&#9654;",  # play symbol
                        "method": "animate",
                    },
                    {
                        "args": [[None], frame_args(0)],
                        "label": "&#9724;",  # pause symbol
                        "method": "animate",
                    },
                ],
                "direction": "left",
                "pad": {"r": 1, "t": 1},
                "type": "buttons",
                "x": 0.1,
                "y": 0,
            }
        ],
        sliders=sliders,
)
    return