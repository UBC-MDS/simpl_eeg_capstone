# -*- coding: utf-8 -*-

"""Module for generating and animating EEG connectivity figures
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mpl_colors
import pandas as pd
import mne
#from mne import compute_covariance
#from mne.connectivity import envelope_correlation, spectral_connectivity
#from mne.viz import circular_layout, plot_connectivity_circle

PAIR_OPTIONS = {
    "all_pairs": [],
    "local_anterior": "Fp1-F7, Fp2-F8, F7-C3, F4-C4, C4-F8, F3-C3",
    "local_posterior": "T5-C3, T5-O1, C3-P3, C4-P4, C4-T6, T6-O2",
    "far_coherence": "Fp1-T5, Fp2-T6, F7-T5, F7-P3, F7-O1, T5-F3, F3-P3, F4-P4, P4-F8, F8-T6, F8-O2, F4-T6",
    "prefrontal_to_frontal_and_central": "Fp1-F3, Fp1-C3, Fp2-F4, Fp2-C4",
    "occipital_to_parietal_and_central": "C3-O1, P3-O1, C4-O2, P4-O4",
    "prefrontal_to_parietal": "Fp1-P3, Fp2-P4",
    "frontal_to_occipital": "F3-O1, P4-O2",
    "prefrontal_to_occipital": "Fp1-O1, Fp2-O2"
}


def convert_pairs(string_pairs):
    """Convert pair names to usable format

    Args:
        string_pairs (str): Comma seperated node pairs in format "node1-node2"

    Returns:
        [tuple]: List of tuples with node pair names
    """
    tuple_pairs = string_pairs
    if type(string_pairs) == str:
        pairs = string_pairs.split(", ")
        tuple_pairs = [tuple(pair.split("-")) for pair in pairs]
    return tuple_pairs


def calculate_connectivity(epoch, calc_type="correlation"):
    """Calculate connectivity between nodes

    Args:
        epoch (mne.epochs.Epochs): Epoch to calculate connectivity for
        calc_type (str, optional): Calculation type, one of spectral_connectivity, envelope_correlation, covariance, correlation. Defaults to "correlation".

    Returns:
        pandas.core.frame.DataFrame: Data frame containing connectivity values
    """
    ch_names = epoch.ch_names

    # only return channel data
    conn_df = epoch.to_data_frame().corr().loc[ch_names, ch_names]

    if calc_type != "correlation":

        if calc_type == "spectral_connectivity":
            conn = mne.connectivity.spectral_connectivity(
                epoch, method="pli", mode="fourier", faverage=True, verbose=False
            )[0][:, :, 0]

        elif calc_type == "envelope_correlation":
            conn = mne.connectivity.envelope_correlation(epoch)

        elif calc_type == "covariance":
            conn = mne.compute_covariance(epoch, verbose=False).data

        else:
            raise Exception("Invalid calculation type")

        conn_df.iloc[-conn.shape[0]:, -conn.shape[1]:] = conn

    return conn_df


def get_frame(epoch, step_size, frame_number):
    """Crop an epoch based on a frame number

    Args:
        epoch (mne.epochs.Epochs): Epoch to crop
        steps (int): Number of time frames per step
        frame_number (int): Current frame number

    Returns:
        mne.epochs.Epochs: Cropped epochs for the given frame
    """
    times = epoch.times
    return epoch.copy().crop(
        times[frame_number],
        times[frame_number+step_size],
        include_tmax=True
    )


def plot_connectivity(data, fig=None, locations=None, calc_type="correlation", pair_list=[], threshold=0, colormap="RdBu_r"):
    """Plot 2d EEG nodes on scalp with lines representing connectivity

    Args:
        data (mne.epochs.Epochs): Epoch to visualize
        fig (matplotlib.pyplot.figure): Figure to plot on
        locations ([matplotlib.text.Text]): List of node locations
        calc_type (str): Connectivity calculation type
        pair_list ([str], optional): List of node pairs. Defaults to [], which indicates all pairs.
        threshold (int, optional): Connectivity threshold to display connection. Defaults to 0.
        colormap (str, optional): Colour scheme to use. Defaults to "RdBlu_r".

    Returns:
        matplotlib.pyplot.figure: Connectivity figure
    """
    if locations is None:
        sensor_locations = data.plot_sensors(show_names=True, show=False);
        locations = sensor_locations.findobj(
            match=lambda x: type(x) == plt.Text and x.get_text() != ""
        )
    if fig is None:
        fig = plt.figure()

    correlation_df = calculate_connectivity(data, calc_type)

    cmap = plt.cm.ScalarMappable(cmap=colormap)
    cmap.set_array(correlation_df)
    cmap.autoscale()

    colour_array = cmap.cmap(correlation_df)

    ax = fig.add_subplot()

    node_df = pd.DataFrame(
        {
            "name": [node.get_text() for node in locations],
            "x": [node.get_position()[0] for node in locations],
            "y": [node.get_position()[1] for node in locations],
        }
    )
    x_list = []
    y_list = []

    for x1, y1, name1 in zip(node_df["x"], node_df["y"], node_df["name"]):
        for x2, y2, name2 in zip(node_df["x"], node_df["y"], node_df["name"]):
            if (name1, name2) in pair_list or not pair_list:
                correlation = correlation_df.loc[name1, name2]
                if abs(correlation) >= threshold:
                    row = correlation_df.columns.get_loc(name1)
                    col = correlation_df.index.get_loc(name2)
                    x_list = [x1, x2]
                    y_list = [y1, y2]
                    ax.plot(
                        x_list,
                        y_list,
                        color=colour_array[row, col],
                        linewidth=0.2/(1-correlation),
                    )
    fig.colorbar(cmap)
    data.plot_sensors(
        axes=ax,
        show_names=True,
        kind="topomap",
        sphere=(9, -12, 0, 100)
    )
    return fig


def animate_connectivity(epoch, calc_type, steps=20, pair_list=[], colormap="RdBlu_r"):
    """Animate 2d EEG nodes on scalp with lines representing connectivity

    Args:
        epochs (mne.epochs.Epochs): Epoch to visualize
        calc_type (str: Connectivity calculation type
        pair_list ([str], optional): List of node pairs. Defaults to [], which indicates all pairs.
        steps (int, optional): Number of frames to use in correlation caluclation. Defaults to 20. 
        colormap (str, optional): Colour scheme to use. Defaults to "RdBlu_r".

    Returns:
        matplotlib.animation.Animation: Animation of connectivity plot
    """

    sensor_locations = epoch.plot_sensors(show_names=True, show=False);
    locations = sensor_locations.findobj(
        match=lambda x: type(x) == plt.Text and x.get_text() != ""
    )

    pair_list = convert_pairs(pair_list)
    num_steps = (len(epoch.times)//steps)-1
    print(num_steps)
    fig = plt.figure()

    def animate(frame_number):
        fig.clear()
        return [
            plot_connectivity(
                get_frame(epoch, num_steps, frame_number),
                fig,
                locations,
                calc_type,
                pair_list=pair_list,
                threshold=0,
                colormap=colormap
            )
        ]
    anim = animation.FuncAnimation(fig, animate, num_steps, blit=True)
    return anim


def plot_conn_circle(epoch, fig, calc_type, max_connections=20, ch_names=[], colormap="RdBu_r", colorbar=True):
    """Plot connectivity circle

    Args:
        epoch (mne.epochs.Epochs): Epoch to visualize
        fig (matplotlib.pyplot.figure): Figure to plot on
        calc_type (str): Connectivity calculation type
        max_connections (int, optional): Maximum connections to plot. Defaults to 50.
        ch_names ([str], optional): List of channel names to display. Defaults to [], which indicates all channels.
        colormap (str, optional): Colour scheme to use. Defaults to "RdBlu_r".
        colormap (bool, optional): Whether to plot the colorbar. Defaults to True.

    Returns:
        matplotlib.pyplot.figure: Connectivity circle figure
    """
    if not ch_names:
        ch_names = epoch.ch_names

    conn = calculate_connectivity(epoch, calc_type=calc_type).loc[
        ch_names,
        ch_names
    ].to_numpy()

    angles = mne.viz.circular_layout(ch_names, ch_names, start_pos=90)

    node_range = list(range(len(ch_names)+4))
    node_cmap = plt.cm.ScalarMappable(cmap="Greys")
    node_cmap.set_array(node_range)
    node_cmap.autoscale()
    node_colors = node_cmap.to_rgba(node_range)

    mne.viz.plot_connectivity_circle(
        conn,
        ch_names,
        n_lines=max_connections,
        fig=fig,
        node_angles=angles,
        facecolor="w",
        textcolor="black",
        colormap=colormap,
        colorbar=colorbar,
        node_colors=[tuple(i) for i in node_colors],
        title="test title"
    )[0]
    return fig


def animate_connectivity_circle(epoch, calc_type, steps=20, colormap="RdBu_r"):
    """Animate connectivity circle

    Args:
        epoch (mne.epochs.Epochs): Epoch to visualize
        calc_type (str: Connectivity calculation type
        steps (int, optional): Number of frames to use in correlation caluclation. Defaults to 20. 
        colormap (str, optional): Colour scheme to use. Defaults to "RdBlu_r".

    Returns:
        matplotlib.animation.Animation: Animation of connectivity plot
    """

    fig = plt.figure()

    def animate(frame_number):
        fig.clear()

        return [
            plot_conn_circle(
                get_frame(epoch, steps, frame_number),
                fig,
                calc_type=calc_type,
                colormap=colormap
            )
        ]

    anim = animation.FuncAnimation(fig, animate, steps, blit=True)
    return anim
