"""Module for generating and animating the topographic map in a 3D head shape
"""

# import libraries
import mne
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.interpolate import NearestNDInterpolator
from simpl_eeg import eeg_objects
import gif


# define the frame arguments for the animated plot
def frame_args(duration):
    """Return the frame arguments of the animated plot

    Args:
        duration (int): The number of frames for the animated plot

    Returns:
        dict: A dictionary of frame arguments
    """

    if type(duration) is not int and type(duration) is not float:
        raise TypeError("duration has to be a number")

    return {
        "frame": {"duration": duration},
        "mode": "immediate",
        "fromcurrent": True,
        "transition": {
            "duration": duration,
            "easing": "linear",
            "redraw": False,
        },  # make sure "redraw" is false to reduce rendering time
    }


def get_standard_coord():
    """Generate an array of cartesian coordinates of the standard node locations ("standard_1005")

    Returns:
        montage (mne.channels.montage): The standard montage from the mne library
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
    """To interpolate EEG signals to locations points that don't have data

    Args:
        df (dataframe): A dataframe that contains the EEG signal of each channels for each time stamps
        channel_names (list): A list of channel names in the raw data
        node_coord (array): A numpy array of (x, y, z) coordinates of all channels in the raw data
        x (array): A numpy array of X coordinates of all channels for interpolation
        y (array): A numpy array of Y coordinates of all channels for interpolation
        z (array): A numpy array of Z coordinates of all channels for interpolation
        t (int): The time stamp we want to interpolate EEG voltages for

    Returns:
        array: A numpy array of interpolated EEG voltages
    """
    if type(df) is not pd.core.frame.DataFrame:
        raise TypeError("df is not a dataframe")

    if type(channel_names) is not list:
        raise TypeError("channel_names has to be a list of names for electrodes")

    if type(node_coord) is not np.ndarray:
        raise TypeError("node_coord has to be a numpy array of electrode names")

    if type(x) is not np.ndarray:
        raise TypeError("x has to be a numpy array of X coordinates for electordes")

    if type(y) is not np.ndarray:
        raise TypeError("y has to be a numpy array of Y coordinates for electordes")

    if type(z) is not np.ndarray:
        raise TypeError("z has to be a numpy array of Z coordinates for electordes")

    # get the EEG data for a specific time stamp
    eeg = df.loc[t, channel_names].values
    # build the interpolation model using NearestNDInterpolator
    interpolate_model = NearestNDInterpolator(node_coord, eeg)
    return interpolate_model(np.array(list(zip(x, y, z))))


def get_eeg_node(raw, standard_montage_list):
    """Get the electrode location from the raw data

    Args:
        raw (mne.epochs.Epochs): The raw epoch data
        standard_montage_list (array): The numpy array which contains the cartesian coordinate of standard node location

    Returns:
        array: The electrode location from the raw data
    """
    if type(raw) is not mne.epochs.Epochs:
        raise TypeError(
            "raw is not an epoched data, please refer to eeg_objects to create an epoched data"
        )

    if type(standard_montage_list) is not mne.channels.montage.DigMontage:
        raise TypeError("standard_montage_list has to be a mne montage")

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
        raw (mne.epochs.Epochs): The raw epoch data
        montage (array): The numpy array which contains the cartesian coordinate of standard node location

    Returns:
        dataframe: A dataframe which contains the electrode name and electrode location from the raw data
    """
    if type(raw) is not mne.epochs.Epochs:
        raise TypeError(
            "raw is not an epoched data, please refer to eeg_objects to create an epoched data"
        )

    if type(montage) is not mne.channels.montage.DigMontage:
        raise TypeError("montage has to be a mne montage")

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


def animate_3d_head(
    epoch,
    plot_title="",
    color_title="EEG MicroVolt",
    color_min=-50,
    color_max=50,
    colormap="Bluered",
):
    """Plot an animated topographic map in a 3D head shape

    Args:
        epoch (mne.epochs.Epochs): An epoched file for the EEGLab data
        plot_title (str, optionl): The title of the plot. Defaults to "".
        color_title (str,  optional): The title of the color bar. Defaults to "EEG MicroVolt".
        color_min (int, optional): The minimum EEG voltage value to be shown on the color bar. Defaults to -50.
        color_max (int, optional): The maximum EEG voltage value to be shown on the color bar. Defaults to 50.
        colormap (str, optional): The colour scheme to use. Defaults to Bluered.

    Returns:
        figure: An animated topographic map in a 3D head shape
    """
    if type(epoch) is not mne.epochs.Epochs:
        raise TypeError(
            "epoch is not an epoched data, please refer to eeg_objects to create an epoched data"
        )

    if type(plot_title) is not str:
        raise TypeError("plot_title has to be a string")

    if type(color_title) is not str:
        raise TypeError("color_title has to be a string")

    if type(colormap) is not str:
        raise TypeError("colormap has to be a string")

    if type(color_min) is not int and type(color_min) is not float:
        raise TypeError("color_min has to be a number")

    if type(color_max) is not int and type(color_max) is not float:
        raise TypeError("color_max has to be a number")

    # find out the channel names
    channel_names = epoch.ch_names

    # change the raw epoched data to a dataframe
    df = epoch.to_data_frame().groupby("time").mean().reset_index()
    df = df.loc[
        (df[channel_names] != 0).all(axis=1)
    ].reset_index()  # remove rows with 0 values for all columns
    nb_frame = len(df)  # calculate the number of frames

    # get the standard montage coordinates
    standard_montage, standard_coord = get_standard_coord()
    x = np.array(standard_coord)[:, 0]
    y = np.array(standard_coord)[:, 1]
    z = np.array(standard_coord)[:, 2]

    # get the coordinates of the electrodes from the raw data
    node_coord = get_eeg_node(epoch, standard_montage)
    node_df = get_node_dataframe(epoch, standard_montage)

    # generate the animated plot
    fig = go.Figure(
        frames=[
            go.Frame(
                data=go.Mesh3d(
                    x=np.array(standard_coord)[:, 0],
                    y=np.array(standard_coord)[:, 1],
                    z=np.array(standard_coord)[:, 2],
                    colorscale=colormap,
                    colorbar_title=color_title,
                    cmin=color_min,
                    cmax=color_max,
                    intensity=interpolated_time(
                        df, channel_names, node_coord, x, y, z, k
                    ),
                    intensitymode="vertex",  # can't be changed
                    alphahull=1,  # can't be changed
                    opacity=1,
                ),
                name=format(
                    epoch.times[k], ".4f"
                ),  # you need to name the frame for the animation to behave properly
            )
            for k in range(nb_frame)
        ]
    )

    # add data to be displayed before animation starts
    fig.add_trace(
        go.Mesh3d(
            x=np.array(standard_coord)[:, 0],
            y=np.array(standard_coord)[:, 1],
            z=np.array(standard_coord)[:, 2],
            colorscale=colormap,
            colorbar_title=color_title,
            cmin=color_min,
            cmax=color_max,
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
        textposition="top center",
        textfont=dict(family="sans serif", size=18),
    )

    # set up slider for the animated plot
    sliders = [
        {
            "pad": {"b": 0, "t": 0},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "currentvalue": {
                "prefix": "Time stamp : ",
                "visible": True,
                "xanchor": "center",
            },
            "steps": [
                {
                    "args": [[f.name], frame_args(0)],
                    "label": f.name + "(s)",
                    "method": "animate",
                }
                for k, f in enumerate(fig.frames)
            ],
            "transition": {"duration": 0, "easing": "linear"},
        }
    ]

    fig.update_layout(
        title=plot_title,
        width=1000,
        height=600,
        scene=dict(
            aspectratio=dict(x=1.5, y=1.5, z=1),
        ),
        updatemenus=[
            {
                "buttons": [
                    {
                        "args": [None, frame_args(0)],
                        "label": "Play",  # play symbol
                        "method": "animate",
                    },
                    {
                        "args": [[None], frame_args(0)],
                        "label": "Pause",  # pause symbol
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
        transition=dict(duration=0, easing="linear"),
    )
    return fig


# generate the 3D topographic map for a single time stamp
def topo_3d_map(
    epoch,
    time_stamp,
    color_title="EEG MicroVolt",
    color_min=-50,
    color_max=50,
    colormap="Bluered",
):
    """Plot a topographic map in a 3D head shape for a single time stamp

    Args:
        epoch (mne.epochs.Epochs): An epoched file for the EEGLab data
        time_stamp (int): The time stamp that is of interest
        color_title (str,  optional): The title of the color bar. Defaults to "EEG MicroVolt".
        color_min (int, optional): The minimum EEG voltage value to be shown on the color bar. Defaults to -50.
        color_max (int, optional): The maximum EEG voltage value to be shown on the color bar. Defaults to 50.
        colormap (str, optional): The colour scheme to use. Defaults to Bluered.

    Returns:
        figure: A topographic map in a 3D head shape
    """
    if type(epoch) is not mne.epochs.Epochs:
        raise TypeError(
            "epoch is not an epoched data, please refer to eeg_objects to create an epoched data"
        )

    if type(color_title) is not str:
        raise TypeError("color_title has to be a string")

    if type(colormap) is not str:
        raise TypeError("colormap has to be a string")

    if type(color_min) is not int and type(color_min) is not float:
        raise TypeError("color_min has to be a number")

    if type(color_max) is not int and type(color_max) is not float:
        raise TypeError("color_max has to be a number")

    # find out the channel names
    channel_names = epoch.ch_names

    # change the raw epoched data to a dataframe
    df = epoch.to_data_frame().groupby("time").mean().reset_index()
    df = df.loc[(df[channel_names] != 0).all(axis=1)].reset_index()
    nb_frame = len(df)

    # get the standard montage coordinates
    standard_montage, standard_coord = get_standard_coord()
    x = np.array(standard_coord)[:, 0]
    y = np.array(standard_coord)[:, 1]
    z = np.array(standard_coord)[:, 2]

    # get the coordinated of the electrodes in the raw data
    node_coord = get_eeg_node(epoch, standard_montage)
    node_df = get_node_dataframe(epoch, standard_montage)

    # get the index
    time_index = df[df["time"] == time_stamp].index.values[0]

    # generate the animated plot
    fig = go.Figure(
        data=go.Mesh3d(
            x=np.array(standard_coord)[:, 0],
            y=np.array(standard_coord)[:, 1],
            z=np.array(standard_coord)[:, 2],
            colorscale=colormap,
            colorbar_title=color_title,
            cmin=color_min,
            cmax=color_max,
            intensity=interpolated_time(
                df, channel_names, node_coord, x, y, z, time_index
            ),
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
        textposition="top center",
        textfont=dict(family="sans serif", size=18),
    )

    # time stamp
    title_time = format(epoch.times[time_index], ".4f")

    fig.update_layout(
        title="Time stamp: " + str(title_time) + "s",
        width=1000,
        height=600,
        scene=dict(
            aspectratio=dict(x=1.5, y=1.5, z=1),
        ),
    )
    return fig


# A helper function to generate gif plotly figure
@gif.frame
def topo3dhead_plot(epoch, i):
    fig = topo_3d_map(epoch, i)
    return fig


# To save the animated plot as a gif
def save_gif(epoch, gifname, duration):
    """Save the animated plot as gif file

    Args:
        epoch(mne.epochs.Epochs): The epoch file for creating gif
        gifname (str): The file name.
        duration (int): The duration (milliseconds) between each frame
    """
    frames = []
    starting = epoch.to_data_frame()["time"].min()
    ending = epoch.to_data_frame()["time"].max()

    # for iterate over each timestamps in the dataframe to generate a plot, and then save it as animated gif
    for i in range(starting, ending, 1):
        frame = topo3dhead_plot(epoch, i)
        frames.append(frame)
    gif.save(frames, f"{gifname}.gif", duration=duration)