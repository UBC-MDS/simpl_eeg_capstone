# -*- coding: utf-8 -*-

"""
Module for reading and generating custom epochs
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import math
import mne

# common node pairs for convenient access
PAIR_OPTIONS = {
    "all_pairs": [],
    "no_pairs": "",
    "local_anterior": "Fp1-F7, Fp2-F8, F7-C3, F4-C4, C4-F8, F3-C3",
    "local_posterior": "T5-C3, T5-O1, C3-P3, C4-P4, C4-T6, T6-O2",
    "far_coherence": (
        "Fp1-T5, Fp2-T6, F7-T5, F7-P3, F7-O1, T5-F3, "
        "F3-P3, F4-P4, P4-F8, F8-T6, F8-O2, F4-T6"
    ),
    "prefrontal_to_frontal_and_central": "Fp1-F3, Fp1-C3, Fp2-F4, Fp2-C4",
    "occipital_to_parietal_and_central": "C3-O1, P3-O1, C4-O2, P4-O4",
    "prefrontal_to_parietal": "Fp1-P3, Fp2-P4",
    "frontal_to_occipital": "F3-O1, P4-O2",
    "prefrontal_to_occipital": "Fp1-O1, Fp2-O2"
}

def convert_pairs(string_pairs):
    """
    Convert pair names to usable format

    Args:
        string_pairs: str
            Comma seperated node pairs in format "node1-node2"

    Returns:
        [tuple]:
            List of tuples with node pair names
    """
    tuple_pairs = string_pairs
    if type(string_pairs) == str:
        pairs = string_pairs.replace(" ", "").split(",")
        tuple_pairs = [tuple(pair.split("-")) for pair in pairs]
    return tuple_pairs


def calculate_connectivity(epoch, calc_type="correlation"):
    """
    Calculate connectivity between nodes

    Args:
        epoch: mne.epochs.Epochs
            Epoch to calculate connectivity for
        calc_type: str (optional)
            Calculation type, one of
            spectral_connectivity,
            envelope_correlation,
            covariance,
            correlation.
            Defaults to "correlation".

    Returns:
        pandas.core.frame.DataFrame:
            Data frame containing connectivity values
    """

    if type(epoch) is not mne.epochs.Epochs and type(epoch) is not mne.evoked.EvokedArray:
        raise TypeError(
            "epoch is not an epoched data, "
            "please refer to eeg_objects to create an epoched data"
        )

    if type(calc_type) is not str:
        raise TypeError("calc_type has to be a string")

    ch_names = epoch.ch_names

    # only return channel data
    conn_df = epoch.to_data_frame().corr().loc[ch_names, ch_names]

    if calc_type != "correlation":

        if calc_type == "spectral_connectivity":
            conn = mne.connectivity.spectral_connectivity(
                epoch,
                method="pli",
                mode="fourier",
                faverage=True,
                verbose=False
            )[0][:, :, 0]

        elif calc_type == "envelope_correlation":
            conn = mne.connectivity.envelope_correlation(epoch)

        elif calc_type == "covariance":
            conn = mne.compute_covariance(epoch, verbose=False).data

        else:
            raise Exception(
                "Invalid calculation type, calc_type can only be one of "
                "correlation, "
                "spectral_connectivity, "
                "envelope_correlation, or"
                "covariance"
            )

        conn_df.iloc[-conn.shape[0]:, -conn.shape[1]:] = conn

    return conn_df

def get_axis_lims_con(epoch):
    """
    Generates an invisible mne.viz.plot_topomap plot and gets the ylim from its
    matplotlib.axes._subplots.AxesSubplot. Helper function for plot_connectivity.
    
    Parameters:
        epoch: mne.epochs.Epochs
            MNE epochs object containing the timestamps.
        
    Returns:
        ax_lims: tuple
            A tuple of the ax_lims.
    """
    fig, ax = plt.subplots()
    
    if type(epoch) is mne.evoked.EvokedArray:
        plot_data = epoch.data[:, 0]
    else:
        plot_data = epoch.get_data('eeg')[0][:, 0]

    mne.viz.plot_topomap(
        data=plot_data,
        pos=epoch.info,
        show=False,
        res=1
    )
    
    axis_lims = ax.get_ylim()
    plt.close()
    return(axis_lims)

def get_frame(epoch, step_size, frame_number):
    """
    Crop an epoch based on a frame number

    Args:
        epoch: mne.epochs.Epochs
            Epoch to crop
        steps_size: int
            Number of time frames per step
        frame_number: int
            Current frame number

    Returns:
        mne.epochs.Epochs:
            Cropped epochs for the given frame
    """
    times = epoch.times
    max_index = len(times)-1
    tmax = (frame_number+1)*step_size

    # make sure we don't go outside the possible range
    if(tmax > max_index):
        tmax = max_index

    return epoch.copy().crop(
        times[frame_number*step_size],
        times[tmax],
        include_tmax=True
    )


def plot_connectivity(
    epoch,
    fig=None,
    locations=None,
    calc_type="correlation",
    pair_list=[],
    threshold=0,
    show_sphere=True,
    readjust_sphere="auto",
    colormap="RdBu_r",
    vmin=None,
    vmax=None,
    line_width=None,
    title=None,
    colorbar=True,
    caption=None,
    **kwargs
):
    """
    Plot 2d EEG nodes on scalp with lines representing connectivity

    Args:
        epoch: mne.epochs.Epochs
            Epoch to visualize
        fig: matplotlib.pyplot.figure (optional)
            Figure to plot on. Defaults to None.
        locations: [matplotlib.text.Text] (optional)
            List of node locations. Defaults to None.
        calc_type: str
            Connectivity calculation type
        pair_list: [str] (optional)
            List of node pairs. Defaults to [], which indicates all pairs.
        threshold: int (optional)
            Unsigned connectivity threshold to display connection.
            Defaults to 0.
        show_sphere: bool (optional)
            Whether to show the cartoon head or not. Defaults to True.
        readjust_sphere: bool or "auto" (optional)
            Tries to re-align cartoon head but may overcorrect. Defaults to "auto".
        colormap: str (optional)
            Colour scheme to use. Defaults to "RdBlu_r".
        vmin: int (optional)
            The minimum for the scale. Defaults to None.
        vmin: int (optional)
            The maximum for the scale. Defaults to None.
        line_width: int (optional)
            The line width for the connections.
            Defaults to None for non-static width.
        title: str (optional)
            The title to display on the plot. Defaults to None for no title.
        colorbar: bool (optional)
            Whether to display the colorbar. Defaults to True.
        caption: str (optional)
            The caption to display at the bottom of the plot. Defaults to None.
        **kwargs: dict (optional)
            Optional arguments to pass to mne.viz.plot_sensors()

            Full list of options available at
            https://mne.tools/stable/generated/mne.viz.plot_sensors.html

    Returns:
        matplotlib.pyplot.figure:
            The generated connectivity figure
    """
    if type(epoch) is not mne.epochs.Epochs and type(epoch) is not mne.evoked.EvokedArray:
        raise TypeError(
            "data is not an epoched data, "
            "please refer to eeg_objects to create an epoched data"
        )

    if locations is None:
        sensor_locations = epoch.plot_sensors(show_names=True, show=False)
        locations = sensor_locations.findobj(
            match=lambda x: type(x) == plt.Text and x.get_text() != ""
        )

    if fig is None:
        fig = plt.figure()

    correlation_df = calculate_connectivity(epoch, calc_type)

    cmap = plt.cm.ScalarMappable(cmap=colormap)

    if vmin is None or vmax is None:
        cmap.set_array(correlation_df)
        cmap.autoscale()
    else:
        cmap.set_clim(vmin, vmax)

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
    width = line_width
    for x1, y1, name1 in zip(node_df["x"], node_df["y"], node_df["name"]):
        for x2, y2, name2 in zip(node_df["x"], node_df["y"], node_df["name"]):
            if (name1, name2) in pair_list or not pair_list:
                correlation = correlation_df.loc[name1, name2]
                if abs(correlation) >= threshold:
                    row = correlation_df.columns.get_loc(name1)
                    col = correlation_df.index.get_loc(name2)
                    x_list = [x1, x2]
                    y_list = [y1, y2]

                    # use width based on connection measure if no width given
                    if not line_width:
                        var_width = math.log(1-min(abs(correlation), 0.999))
                        width = 1.5 + var_width

                    ax.plot(
                        x_list,
                        y_list,
                        color=colour_array[row, col],
                        linewidth=width
                    )

    # add padding for names
    epoch.copy()
    epoch = epoch.rename_channels(lambda x: "  "+str(x))

    # Default to no sphere values
    sphere_vals = None

    # If sphere parameters have not been provided by user...
    if show_sphere and 'sphere' not in locals():
        # get axis limits
        ax_lims = get_axis_lims_con(epoch)

        def_sphere = ax_lims[0]*-0.94

        # Attempt to determine whether to readjust sphere or not based
        # on the limits of the axis
        if readjust_sphere=="auto":
            if ax_lims[0] <= -50:
                readjust_sphere=True
            else:
                readjust_sphere=False
        
        # Readjust with Cz node at center if it is present
        if readjust_sphere:
            if 'Cz' in node_df['name']:
                def_x = node_df[node_df['name'] == 'Cz']['x']
                def_y = node_df[node_df['name'] == 'Cz']['y']
            else:
                def_x = node_df['x'].mean()
                def_y = node_df['y'].mean()
        else:
            def_x = 0.0
            def_y = 0.0
        
        sphere_vals = (def_x, def_y, 0.0, def_sphere)

    # combine default settings with user specified settings
    default_kwargs = {
        "axes": ax,
        "show_names": True,
        "kind": "topomap",
        "sphere": sphere_vals,
        "show": False
    }

    if show_sphere==False:
        default_kwargs.pop('sphere', None)

    kwargs = {**default_kwargs, **kwargs}

    epoch.plot_sensors(**kwargs)

    if colorbar:
        fig.colorbar(cmap)

    if title:
        plt.title(title)

    if caption:
        if 'ax_lims' not in locals():
            ax_lims = get_axis_lims_con(epoch)
        if ax_lims[0] <= -50:
            plt.text(ax_lims[0]*0.45, -ax_lims[1] - ax_lims[1]*0.25, caption, fontsize=10)
        else:
            plt.text(ax_lims[0]*0.45, -ax_lims[1], caption, fontsize=10)

    return fig


def animate_connectivity(
    epoch,
    calc_type="correlation",
    steps=20,
    pair_list=[],
    threshold=0,
    show_sphere=True,
    colormap="RdBu_r",
    vmin=None,
    vmax=None,
    line_width=None,
    title=None,
    colorbar=True,
    timestamp=True,
    frame_rate=12.0,
    **kwargs
):
    """
    Animate 2d EEG nodes on scalp with lines representing connectivity

    Args:
        epochs: mne.epochs.Epochs
            Epoch to visualize
        calc_type: str (optional)
            Connectivity calculation type. Defaults to "correlation".
        steps: int (optional)
            Number of frames to use in correlation caluclation. Defaults to 20.
        pair_list: [str] (optional)
            List of node pairs. Defaults to [], which indicates all pairs.
        threshold: int (optional)
            Unsigned connectivity threshold to display connection.
            Defaults to 0.
        show_sphere: bool (optional)
            Whether to show the cartoon head or not. Defaults to True.
        colormap: str (optional)
            Colour scheme to use. Defaults to "RdBu_r"
        vmin: int (optional)
            The minimum for the scale. Defaults to None.
        vmin: int (optional)
            The maximum for the scale. Defaults to None.
        line_width: int (optional)
            The line width for the connections.
            Defaults to None for non-static width.
        title: str (optional)
            The title to display on the plot. Defaults to None for no title.
        colorbar: bool (optional)
            Whether to show the colorbar. Defaults to True.
        timestamp: bool (optional)
            Whether to show the timestamp caption. Defaults to True.
        frame_rate: int or float (optional)
            The frame rate to genearte the final animation with. Defaults to 12.0.
        **kwargs: dict (optional)
            Optional arguments to pass to mne.viz.plot_sensors()

            Full list of options available at
            https://mne.tools/stable/generated/mne.viz.plot_sensors.html

    Returns:
        matplotlib.animation.Animation:
            Animation of connectivity plot
    """
    if type(epoch) is not mne.epochs.Epochs and type(epoch) is not mne.evoked.EvokedArray:
        raise TypeError(
            "epoch is not an epoched data, "
            "please refer to eeg_objects to create an epoched data"
        )
    
    if type(frame_rate) is not int and type(frame_rate) is not float:
        raise TypeError(
                """Passed frame_rate object is not in the correct format, 
                please pass an int or float instead"""
            )

    sensor_locations = epoch.plot_sensors(show_names=True, show=False)
    locations = sensor_locations.findobj(
        match=lambda x: type(x) == plt.Text and x.get_text() != ""
    )

    pair_list = convert_pairs(pair_list)
    num_steps = math.ceil(len(epoch.times)/steps)
    ms_between_frames = 1000 / frame_rate

    fig = plt.figure()

    def animate(frame_number):
        fig.clear()

        frame_epoch = get_frame(epoch, steps, frame_number)

        start_time = frame_epoch.tmin
        end_time = frame_epoch.tmax

        caption = None
        if timestamp is True:
            start_space=''
            end_space=''
            if start_time > 0:
                start_space=' '
            if end_time > 0:
                end_space=' '

            caption = f"time: {start_space}{'%.3f' % start_time}s to {end_space}{'%.3f' % end_time}s"

        return [
            plot_connectivity(
                frame_epoch,
                fig,
                locations,
                calc_type,
                pair_list=pair_list,
                threshold=threshold,
                show_sphere=show_sphere,
                colormap=colormap,
                vmin=vmin,
                vmax=vmax,
                line_width=line_width,
                title=title,
                colorbar=colorbar,
                caption=caption,
                **kwargs
            )
        ]
    anim = animation.FuncAnimation(
        fig,
        animate,
        num_steps,
        interval = ms_between_frames,
        blit=True
    )
    return anim


def plot_conn_circle(
    epoch,
    fig=None,
    calc_type="correlation",
    max_connections=50,
    ch_names=[],
    colormap="RdBu_r",
    vmin=None,
    vmax=None,
    line_width=1.5,
    title=None,
    colorbar=True,
    caption=None,
    **kwargs
):
    """
    Plot connectivity circle

    Args:
        epoch: mne.epochs.Epochs
            Epoch to visualize
        fig: matplotlib.pyplot.figure (optional)
            Figure to plot on. Defaults to None.
        calc_type: str (optional)
            Connectivity calculation type. Defaults to "correlation"
        max_connections: int (optional)
            Maximum connections to plot. Defaults to 50.
        ch_names: [str] (optional)
            List of channel names to display.
            Defaults to [], which indicates all channels.
        vmin: int (optional)
            The minimum for the scale. Defaults to None.
        vmin: int (optional)
            The maximum for the scale. Defaults to None.
        colormap: str (optional)
            Colour scheme to use. Defaults to "RdBu_r".
        colormap: bool (optional)
            Whether to plot the colorbar. Defaults to True.
        line_width: int (optional)
            The line width for the connections. Defaults to 1.5.
        title: str (optional)
            The title to display on the plot. Defaults to None for no title.
        colorbar: bool (optional)
            Whether to display the colorbar or not. Defaults to True.
        caption: str (optional)
            The caption to display at the bottom of the plot. Defaults to None.
        **kwargs: dict (optional)
            Optional arguments to pass to mne.viz.plot_connectivity_circle()

            Full list of options available at
            https://mne.tools/stable/generated/mne.viz.plot_connectivity_circle.html

    Returns:
        matplotlib.pyplot.figure:
            Connectivity circle figure
    """
    if type(epoch) is not mne.epochs.Epochs and type(epoch) is not mne.evoked.EvokedArray:
        raise TypeError(
            "epoch is not an epoched data, "
            "please refer to eeg_objects to create an epoched data"
        )

    if not fig:
        fig = plt.figure()

    if not ch_names:
        ch_names = epoch.ch_names

    conn = calculate_connectivity(epoch, calc_type=calc_type).loc[
        ch_names,
        ch_names
    ].to_numpy()

    angles = mne.viz.circular_layout(ch_names, ch_names, start_pos=90)

    # combine default settings with user specified settings
    default_kwargs = {
        "n_lines": max_connections,
        "fig": fig,
        "node_angles": angles,
        "facecolor": "w",
        "textcolor": "black",
        "colormap": colormap,
        "node_colors": ["grey" for i in range(len(ch_names))],
        "vmin": vmin,
        "vmax": vmax,
        "linewidth": line_width,
        "title": title
    }
    kwargs = {**default_kwargs, **kwargs}

    fig = mne.viz.plot_connectivity_circle(
        conn,
        ch_names,
        colorbar=False,
        **kwargs
    )[0]

    if colorbar:
        cmap = plt.cm.ScalarMappable(cmap=colormap)
        cmap.set_clim(vmin, vmax)
        fig.colorbar(cmap)

    if caption:
        fig.text(0.33, 0.1, caption, fontsize=10)

    return fig


def animate_connectivity_circle(
    epoch,
    calc_type="correlation",
    max_connections=50,
    steps=20,
    colormap="RdBu_r",
    vmin=None,
    vmax=None,
    line_width=1.5,
    title=None,
    colorbar=True,
    timestamp=True,
    frame_rate = 12.0,
    **kwargs
):
    """
    Animate connectivity circle

    Args:
        epoch: mne.epochs.Epochs
            Epoch to visualize
        calc_type: str (optional)
            Connectivity calculation type. Defaults to "correlation".
        max_connections: int (optional)
            Number of connections to display. Defaults to 50.
        steps: int (optional)
            Number of frames to use in correlation caluclation. Defaults to 20.
        colormap: str (optional)
            Colour scheme to use. Defaults to "RdBu_r".
        vmin: int (optional)
            The minimum for the scale. Defaults to None.
        vmin: int (optional)
            The maximum for the scale. Defaults to None.
        line_width: int (optional)
            The line width for the connections. Defaults to 1.5.
        title: str (optional)
            The title to display on the plot. Defaults to None for no title.
        colorbar: bool (optional)
            Whether to display the colorbar or not. Defaults to True.
        timestamp: bool (optional)
            Whether to display the timestamp caption. Defaults to True.
        frame_rate: int or float (optional)
            The frame rate to genearte the final animation with. Defaults to 12.0.
        **kwargs: dict (optional)
            Optional arguments to pass to mne.viz.plot_connectivity_circle()

            Full list of options available at
            https://mne.tools/stable/generated/mne.viz.plot_connectivity_circle.html

    Returns:
        matplotlib.animation.Animation:
            Animation of connectivity plot
    """
    if type(epoch) is not mne.epochs.Epochs and type(epoch) is not mne.evoked.EvokedArray:
        raise TypeError(
            "epoch is not an epoched data, "
            "please refer to eeg_objects to create an epoched data"
        )
    
    if type(frame_rate) is not int and type(frame_rate) is not float:
        raise TypeError(
                """Passed frame_rate object is not in the correct format, 
                please pass an int or float instead"""
            )
    
    ms_between_frames = 1000 / frame_rate

    fig = plt.figure()

    num_steps = math.ceil(len(epoch.times)/steps)

    # combine default settings with user specified settings
    default_kwargs = {
        "calc_type": calc_type,
        "max_connections": max_connections,
        "colormap": colormap,
        "vmin": vmin,
        "vmax": vmax,
        "line_width": line_width,
        "title": title
    }
    kwargs = {**default_kwargs, **kwargs}

    def animate(frame_number):
        fig.clear()

        frame_epoch = get_frame(epoch, steps, frame_number)

        start_time = frame_epoch.tmin
        end_time = frame_epoch.tmax

        caption = None
        if timestamp is True:
            caption = f"time: {'%.3f' % start_time}s to {'%.3f' % end_time}s"

        return [
            plot_conn_circle(
                frame_epoch,
                fig,
                colorbar=colorbar,
                caption=caption,
                **kwargs
            )
        ]

    anim = animation.FuncAnimation(
        fig,
        animate,
        num_steps,
        interval = ms_between_frames,
        blit=True
    )
    return anim
