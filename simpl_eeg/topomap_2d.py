import matplotlib.pyplot as plt
import matplotlib.animation as animation
import mne
import numpy
import numpy as np
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from pylab import text


def add_timestamp(epoch, x_pos, y_pos, frame_number):
    """
    Adds a timestamp to a matplotlib.image.AxesImage object.
    
    Parameters:
        epoch: mne.epochs.Epochs
            MNE epochs object containing the timestamps.
        ax_lims: tuple
            A tuple of the ax_lims.
        frame_number: int
            The timestamp to plot.
    """
    
    frame_time = epoch.times[frame_number]
    tstamp = format(frame_time, '.4f')
    
    if frame_time >= 0:
        text(x_pos, y_pos, 'time:  {}'.format(tstamp) + 's')
    else:
        text(x_pos, y_pos, 'time: {}'.format(tstamp) + 's')
    
        
        
def get_axis_lims(epoch):
    """
    Generates an invisible mne.viz.plot_topomap plot and gets the ylim from its
    matplotlib.axes._subplots.AxesSubplot.
    
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


def plot_topomap_2d(epoch,
                    plotting_data=None,
                    recording_number=0,
                    colormap='RdBu_r',
                    colorbar=True,
                    vmin = -30, 
                    vmax = 30,
                    mark='dot',
                    sphere='auto',
                    timestamp = True,
                    **kwargs
                    ):
    """
    Plots a still image mne.epochs.Epochs EEG data as a 2D topomap using the mne.viz.plot_topomap
    function.

    Parameters:
        epoch: mne.epochs.Epochs or mne.evoked.EvokedArray
            MNE epochs object (or evoked array object) containing portions of raw EEG data built
            around specified timestamp(s).
        plotting_data: numpy.ndarray or None
            Array of the EEG data from a measurement (not a time interval) to be plotted should be in
            the format (num_channels, ) i.e. a single row of values for the only timestamp you plan
            to plot. If plotting_data is provided the heatmap in the figure will be built from it in
            conjunction with the 'info' from the provided epoch (containing information like node
            names and locations). If no plotting_data is provided the heatmap will be built from the
            EEG data in the epoch instead. Defaults to None.
        recording_number: int
            The index of the data recording in the epoch to show in the plot. Defaults to 0.
        colormap: matplotlib colormap or None
            Specifies the 'colormap' parameter to be used in the mne.viz.plot_topomap() and
            in colorbar generation. Defaults to 'RdBu_r'.
        colorbar: bool
            Specifies whether to include a colorbar or not. Removing it will marginally improve
            performance. Defaults to True.
        vmin: float
            Specifies the 'vmin' parameter in the mne.viz.plot_topomap() function.
            Sets the limits for the colors which will be used on the topomap. Value is
            in ??V. Defaults to -30.
        vmax: float
            Specifies the 'vmax' parameter in the mne.viz.plot_topomap() function.
            Sets the limits for the colors which will be used on the topomap. Value is
            in ??V. Defaults to +30.
        mark: str
            Specifies what kind of marker should be shown for each node on the topomap. Can be one of
            'dot', 'r+' (for red +'s), 'channel_name', or 'none'. Deaults to 'dot'.
        timestamp: bool
            Specifies whether or not to show the timestamp on the plot relative to the time in the epoch that
            is being shown. Defaults to True.
        **kwargs: various
            Additional arguments from the 'mne.viz.plot_topomap' function
            (https://mne.tools/stable/generated/mne.viz.plot_topomap.html) may also be passed. Since this function
            is used under-the-hood most of these arguments should work exactly as they do in their original
            function. The exact list of avalible arguments and their defaults includes: [contours: 0, sphere: 100,
            res: 64, extrapolate: 'head', outlines: 'head, mask: None, mask_params: None, image_interp: 'blinear',
            show: False, onselect: None, border: 'mean', ch_type: 'eeg', axes: None]. Some arguments may break
            this function. The arguments that are tested and known to work include [res, sphere, extrapolate,
            outlines, contours, outlines, border].

    Returns:
        topo_2d_fig: matplotlib.image.AxesImage
            matplotlib image plot of a 2d topographic map based on the input epoch data.
    """

    defaultKwargs = {'contours': 0, 'res': 64, 'extrapolate': 'head', 'outlines': 'head',
                    'axes': None, 'mask': None, 'mask_params': None, 'image_interp': 'bilinear', 'show': False,
                    'onselect': None, 'border': 'mean', 'ch_type': 'eeg'}
    kwargs = { **defaultKwargs, **kwargs }    
    
    if type(plotting_data) != numpy.ndarray and plotting_data is not None:
        raise TypeError(
            """Passed plotting_data object is not in the correct format, 
            please pass an numpy.ndarray object instead"""
        )
    
    if type(recording_number) != int:
        raise TypeError(
            """Passed plotting_data object is not in the correct format, 
            please pass an int instead"""
        )
    
    if type(epoch) is not mne.epochs.Epochs and type(epoch) is not mne.evoked.EvokedArray:
        raise TypeError(
            """Passed epoch object is not in the correct format, 
            please pass an mne.epochs.Epochs or mne.evoked.EvokedArray object instead"""
        )
    
    if type(epoch) is mne.epochs.Epochs:
        if len(epoch.events) > 1:
            raise Warning(
                """Epoch with multiple events passed. The first event will be used to
                generate the plot. If you wish to see a specific event_number please pass
                epoch[event_number]. If you wish to see an averaged version of all of
                your epochs please pass evoked data instead (generated using 
                `evoked = epoch.average()`)"""
            )
    
    if mark not in ['dot', 'r+', 'channel_name', 'none']:
        raise ValueError(
                """Passed mark is not accepted, please pass one of 'dot', 'r+',
                'channel_name', or 'none'"""
            )
    
    if type(timestamp) is not bool and timestamp is not None:
        raise TypeError(
                """Passed timestamp object is not in the correct format, 
                please pass a bool (True or False) instead"""
            )
    
    if type(colorbar) is not bool:
        raise TypeError(
                """Passed colorbar object is not in the correct format, 
                please pass a bool (True or False) instead"""
            )
    
    if plotting_data is None:
        if isinstance(epoch, mne.epochs.Epochs):
            plotting_data = epoch.get_data('eeg')[0][:, recording_number]
        elif isinstance(epoch, mne.evoked.EvokedArray):
            plotting_data = epoch.data[:, recording_number]
    
    if type(plotting_data) == numpy.ndarray:
        if type(epoch) is mne.epochs.Epochs:
            if plotting_data.shape[0] != epoch.get_data('eeg').shape[1]:
                raise ValueError(
                    """Passed plotting_data object does not match the number of channels in the epoch data. 
                    Please pass a numpy.ndarray of a single set of voltage readings for each node used in the data.
                    For example, if your data has 19 channels, then the shape should be (19,)"""
                )
        if len(plotting_data.shape) > 1:
            raise ValueError(
                """Passed plotting_data object contains more than a single row. 
                Please pass a numpy.ndarray of a single set of voltage readings for each node used in the data.
                For example, if your data has 19 channels, then the shape should be (19,)"""
            )

    # Variables used to determine mark type
    names_value = False
    sensor_value = True
    show_names_value = False
    if mark == 'r+':
        sensor_value = 'r+'
    if mark == 'channel_name':
        names_value = epoch.ch_names
        show_names_value = True
        sensor_value = False
    if mark == 'none':
        sensor_value = False

    # Only make a new figure/axis if needed for additional elements
    if colorbar or timestamp:
        fig, ax = plt.subplots()
    
    if colorbar or timestamp or sphere=="auto":
        ax_lims = get_axis_lims(epoch)

    if sphere=="auto":
        sphere=ax_lims[0] * -0.95

    try:
        topo_2d_fig = mne.viz.plot_topomap(
            data=plotting_data,
            pos=epoch.info,  # Location info for data points
            vmin=vmin / 1e6,  # Convert back to volts
            vmax=vmax / 1e6,
            cmap=colormap, 
            sensors=sensor_value,  
            names=names_value, 
            show_names=show_names_value,
            sphere=sphere,
            **kwargs
        )[0]
    except:
        # Sphere parameter breaks plot if pre-loaded montage is used
        topo_2d_fig = mne.viz.plot_topomap(
            data=plotting_data,
            pos=epoch.info, 
            vmin=vmin / 1e6, 
            vmax=vmax / 1e6,
            cmap=colormap, 
            sensors=sensor_value,  
            names=names_value, 
            show_names=show_names_value,
            **kwargs
        )[0]
        # if sphere != 'auto':
        #     raise Warning(
        #         """Entered sphere parameter not used since it is not compatible with
        #         the montage in the passed epoch."""
        #     )
    
    if timestamp:
        add_timestamp(epoch, ax_lims[0]*0.25, -ax_lims[1] - ax_lims[1]*0.3, recording_number)
        
    if colorbar:
        ax_divider = make_axes_locatable(ax)
        cax = ax_divider.append_axes("right", size=0.1, pad="0%")
        vmid = (vmin+vmax)/2
        clim = dict(kind='value', lims=[vmin, vmid, vmax])
        # https://mne.tools/stable/generated/mne.viz.plot_brain_colorbar.html
        mne.viz.plot_brain_colorbar(
            cax,
            clim,
            colormap=colormap,
            transparent=False,
            orientation='vertical',
            label='??V',
            bgcolor='0'
        )
    
    return topo_2d_fig


def animate_topomap_2d(epoch,
                       plotting_data=None,
                       colormap='RdBu_r',
                       mark='dot',
                       vmin=-30,
                       vmax = 30,
                       sphere = 'auto',
                       colorbar=True,
                       timestamp=True,
                       frame_rate=12,
                       **kwargs):
    """
    Plots a still image mne.epochs.Epochs EEG data as a 2D topomap using the mne.viz.plot_topomap
    function.

    Parameters:
        epoch: mne.epochs.Epochs or mne.evoked.EvokedArray
            MNE epochs object (or evoked array object) containing portions of raw EEG data built
            around specified timestamp(s).
        plotting_data: numpy.ndarray or None
            Array of the EEG data from a measurement (not a time interval) to be plotted should be in
            the format (num_channels, num_frames) i.e. multiple rows of values for the timestamps you plan
            to plot. If plotting_data is provided the heatmap in the figure will be built from it in
            conjunction with the 'info' from the provided epoch (containing information like node names
            and locations). If no plotting_data is provided the heatmap will be built from the EEG data
            in the epoch instead.
        colormap: matplotlib colormap or None
            Specifies the 'colormap' parameter to be used in the mne.viz.plot_topomap() and
            in colorbar generation. Defaults to 'RdBu_r'.
        mark: str
            Specifies what kind of marker should be shown for each node on the topomap. Can be one of
            'dot', 'r+' (for red +'s), 'channel_name', or 'none'. Defaults to 'dot'.
        vmin: float
            Specifies the 'vmin' parameter in the mne.viz.plot_topomap() function.
            Sets the limits for the colors which will be used on the topomap. Value is
            in ??V. Defaults to -30.
        vmax: float
            Specifies the 'vmax' parameter in the mne.viz.plot_topomap() function.
            Sets the limits for the colors which will be used on the topomap. Value is
            in ??V. Defaults to +30.
        colorbar: bool
            Specifies whether or not to include a colorbar in the animation. Removing will lead to
            a marginal decrease in rendering times. Defaults to True.
        timestamp: bool
            Specifies whether or not to show the timestamp on the plot relative to the time in the epoch that
            is being shown. Defaults to True.
        frame_rate: int or float
            The frame rate to genearte the final animation with. Defaults to 12.
        **kwargs: various
            Additional arguments from the 'mne.viz.plot_topomap' function
            (https://mne.tools/stable/generated/mne.viz.plot_topomap.html) may also be passed. Since this function
            is used under-the-hood most of these arguments should work exactly as they do in their original
            function. The exact list of avalible arguments and their defaults includes: [contours: 0, sphere: 100,
            res: 64, extrapolate: 'head', outlines: 'head, mask: None, mask_params: None, image_interp: 'blinear',
            show: False, onselect: None, border: 'mean', ch_type: 'eeg']. The 'axes' argument is not avalible
            since it does not work with animations. Some arguments may break this function. The arguments that are
            tested and known to work include [res, sphere, extrapolate, outlines, contours, outlines, and border].

    Returns:
        ani: matplotlib.animation.FuncAnimation
            matplotlib funcanimation of a 2d topographic map based on the input epoch data.
    """

    defaultKwargs = {'contours': 0, 'res': 64, 'extrapolate': 'head', 'outlines': 'head',
                    'mask': None, 'mask_params': None, 'image_interp': 'bilinear', 'show': False,
                    'onselect': None, 'border': 'mean', 'ch_type': 'eeg'}
    kwargs = { **defaultKwargs, **kwargs }   

    if type(frame_rate) is not int and type(frame_rate) is not float:
        raise TypeError(
                """Passed frame_rate object is not in the correct format, 
                please pass an int or float instead"""
            )
    
    if type(timestamp) is not bool:
        raise TypeError(
                """Passed timestamp object is not in the correct format, 
                please pass a bool (True or False) instead"""
            )
    
    if type(colorbar) is not bool:
        raise TypeError(
                """Passed colorbar object is not in the correct format, 
                please pass a bool (True or False) instead"""
            )
    
    if type(plotting_data) is not numpy.ndarray and plotting_data is not None:
        raise TypeError(
                """Passed plotting_data object is not in the correct format, 
                please pass a numpy.ndarray instead"""
            )
    
    if type(epoch) is mne.epochs.Epochs:
        if len(epoch.events) > 1:
            raise Warning(
                """Epoch with multiple events passed. The first event will be used to
                generate the plot. If you wish to see a specific event_number please pass
                epoch[event_number]. If you wish to see an averaged version of all of
                your epochs please pass evoked data instead (generated using 
                `evoked = epoch.average()`)"""
            )

    # Get plotting data into correct format depending on user input
    if type(plotting_data) == numpy.ndarray:
        frames_to_show = np.arange(0, plotting_data.shape[1], 1)
    elif isinstance(epoch, mne.epochs.Epochs):
        frames_to_show = np.arange(0, epoch.get_data('eeg')[0].shape[1], 1)
        plotting_data = epoch.get_data('eeg')[0]
    elif isinstance(epoch, mne.evoked.EvokedArray):
        frames_to_show = np.arange(0, epoch.data.shape[1], 1)
        plotting_data = epoch.data
    
    ms_between_frames = 1000 / frame_rate
    fig, ax = plt.subplots()

    # Need to get the axis scale since it varies with different data
    if colorbar or timestamps or sphere=="auto":
        ax_lims = get_axis_lims(epoch)
    
    if sphere=="auto":
        sphere=ax_lims[0] * -0.95
    
    if colorbar:
        ax_divider = make_axes_locatable(ax)
        vmid = (vmin+vmax)/2
        clim = dict(kind='value', lims=[vmin, vmid, vmax])

    # Internal animation function to be called later
    def animate(frame_number):
        #if frame_number != 0:
        fig.clear()
        ax.clear()
        
        topomap_2d = plot_topomap_2d(
            epoch=epoch,
            plotting_data=plotting_data[:, frame_number],
            colormap=colormap,
            mark=mark,
            vmin = vmin,
            vmax = vmax,
            timestamp = False,
            colorbar=False,
            sphere=sphere,
            **kwargs
        )
        
        if timestamp:
            add_timestamp(epoch, ax_lims[0], ax_lims[1], frame_number)

        if colorbar:
            cax = ax_divider.append_axes("right", size=0.1, pad="0%")
            # https://mne.tools/stable/generated/mne.viz.plot_brain_colorbar.html
            mne.viz.plot_brain_colorbar(
                cax,
                clim,
                colormap=colormap,
                transparent=False,
                orientation='vertical',
                label='??V',
                bgcolor='0'
            )
        
            
        return [fig]

    ani = animation.FuncAnimation(
        fig,
        animate,
        frames=frames_to_show,
        interval=ms_between_frames,
        blit=True
    )

    return ani