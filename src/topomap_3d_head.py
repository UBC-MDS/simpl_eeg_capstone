"""Module for generating and animating the topographic map in a 3D head shape
"""

# import libraries
import mne
import numpy as np
import pandas as pd
import plotly
import plotly.graph_objects as go
import scipy.io
from scipy.interpolate import NearestNDInterpolator


def frame_args(duration):
    """Return the frame arguments of the animated plot

    Args:
        duration (int): The number of time stamps for the animated plot

    Returns:
        dict: A dictionary of frame arguments
    """
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
    # get the dictionary of standard montage "standard_1005"
    montage = mne.channels.make_standard_montage("standard_1005")
    standard_coord_list = []
    # get the cartesian coordinates from the standard montage dictionary
    for key, value in montage.get_positions()["ch_pos"].items():
        standard_coord_list.append(value.tolist())
    # save the cartesian coordinates in a numpy array
    standard_coord_array = np.array(standard_coord_list)
    return montage, standard_coord_array


def interpolated_time(df, channel_names, node_coord, x, y, z, t):
    """The function to animate the 3D plot

    Args:
        df (dataframe): A dataframe that contains the EEG signal of each electrodes for each time stamps
        channel_names (list): A list of channel names
        node_coord (array): A numpy array of (x, y, z) coordinates of all nodes
        x (array): A numpy array of X coordinates of all nodes for interpolation
        y (array): A numpy array of Y coordinates of all nodes for interpolation
        z (array): A numpy array of Z coordinates of all nodes for interpolation
        t (int): The time stampe we want to interpolate EEG voltages for

    Returns:
        array: A numpy array of interpolated EEG voltages
    """
    # get the EEG data for a specific time stamp
    now = df[df["time"] == t]
    # slice the dataframe to only include EEG signals of each electrodes
    eeg = now.loc[:, channel_names].mean().values
    # build the interpolation model using NearestNDInterpolator
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
        node_list.append(
            standard_montage_list.get_positions()["ch_pos"][channel].tolist()
        )
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
                montage.get_positions()["ch_pos"][channel][0],  # x value
                montage.get_positions()["ch_pos"][channel][1],  # y value
                montage.get_positions()["ch_pos"][channel][2],  # z value
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
    # read in the data and store it in a dataframe
    raw_data = mne.io.read_raw_eeglab(raw)
    raw_df = raw_data.to_data_frame()

    # find out the channel names
    channel_names = raw_data.ch_names

    # slice the dataframe to only include EEG data for the specified time frame
    df = raw_df[(raw_df["time"] > starting) & (raw_df["time"] < ending)]

    # get the standard montage coordinates
    standard_montage, standard_coord = get_standard_coord()
    x = np.array(standard_coord)[:, 0]
    y = np.array(standard_coord)[:, 1]
    z = np.array(standard_coord)[:, 2]

    # get the coordinated of the electrodes in the raw data
    node_coord = get_eeg_node(raw_data, standard_montage)
    nb_frames = duration
    node_df = get_node_dataframe(raw_data, standard_montage)

    # generate the animated plot
    fig = go.Figure(
        frames=[
            go.Frame(
                data=go.Mesh3d(
                    x=np.array(standard_coord)[:, 0],
                    y=np.array(standard_coord)[:, 1],
                    z=np.array(standard_coord)[:, 2],
                    colorscale="Bluered",
                    colorbar_title="EEG Voltage",
                    intensity=interpolated_time(
                        df, channel_names, node_coord, x, y, z, k
                    ),
                    intensitymode="vertex",
                    alphahull=1,
                    opacity=1,
                ),
                name=str(
                    k
                ),  # you need to name the frame for the animation to behave properly
            )
            for k in range(nb_frames)
        ]
    )

    # add data to be displayed before animation starts
    fig.add_trace(
        go.Mesh3d(
            x=np.array(standard_coord)[:, 0],
            y=np.array(standard_coord)[:, 1],
            z=np.array(standard_coord)[:, 2],
            colorscale="Bluered",
            colorbar_title="EEG Voltage",
            intensity=interpolated_time(df, channel_names, node_coord, x, y, z, 0),
            intensitymode="vertex",
            alphahull=1,
            opacity=1,
        )
    )

    # add the 3D scatter plot for the electrodes of the raw data
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

    # set up slider for the animated plot
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
    fig.show()