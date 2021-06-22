import matplotlib.pyplot as plt
import matplotlib.animation as animation
import mne
import numpy
import numpy as np
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable


def add_timestamp(epoch, frame_number, xpos, ypos):
    """
    Adds a timestamp to a matplotlib.image.AxesImage object
    
    Parameters:
        epoch : mne.epochs.Epochs
            MNE epochs object containing the timestamps.

        frame_number: int
            The timestamp to plot.
        
        xpos: float
            The matplotlib x coordinate of the timestamp.

        ypos: float
            The matplotlib y coordinate of the timestamp.
        
    Returns:
    """
    
    time = epoch.times[frame_number]
    tstamp = format(time, '.4f')
    if time >= 0:
        plt.text(-35, -130, 'time:  {}'.format(tstamp) + 's', fontsize=10)
    else:
        plt.text(-35, -130, 'time: {}'.format(tstamp) + 's', fontsize=10)


def plot_topomap_2d(epoch,
                    plotting_data=None,
                    recording_number=0,
                    colormap='RdBu_r',
                    colorbar=True,
                    cmin = -30, 
                    cmax = 30,
                    mark='dot',
                    timestamp = True,
                    **kwargs
                    ):
    """
    Plots a still image mne.epochs.Epochs EEG data as a 2D topomap using the mne.viz.plot_topomap
    function.

    Parameters:
        epoch: mne.epochs.Epochs
            MNE epochs object containing portions of raw EEG data built around specified timestamp(s)

        plotting_data: numpy.ndarray or None
            Array of the EEG data from a measurement (not a time interval) to be plotted should be in
            the format (num_channels, ) i.e. a single row of values for the only timestamp you plan
            to plot.
        
        recording_number: int
            The "frame" of the epoch to show in the plot.

        colormap: matplotlib colormap or None
            Specifies the 'colormap' parameter in the mne.viz.plot_topomap() function.
        
        colorbar: bool
            Specifies whether to include a colorbar or not. Removing it will improve performance.
        
        cmin: float
            Specifies the 'vmin' parameter in the mne.viz.plot_topomap() function.
            Sets the limits for the colors which will be used on the topomap. Value is
            in μV. Defaults to -10.
            
        cmax: float
            Specifies the 'vmax' parameter in the mne.viz.plot_topomap() function.
            Sets the limits for the colors which will be used on the topomap. Value is
            in μV. Defaults to +10.

        mark: str
            Specifies what kind of marker should be shown for each node on the topomap. Can be one of
            'dot', 'r+' (for red +'s), 'channel_name', or 'none'.
            
        timestamp: bool
            Specifies whether or not to show the timestamp on the plot relative to the time in the epoch that
            is being shown. Defaults to true.
        
        **kwargs: various
            Additional arguments from the 'mne.viz.plot_topomap' function
            (https://mne.tools/stable/generated/mne.viz.plot_topomap.html) may be provided. Since this function
            is used under the hood most of these arguments should work exactly as they do in their original
            function. The exact list of avalible arguments includes: [contours, sphere, res, extrapolate, outlines,
            axes, mask, mask_params, image_interp, show, onselect, border, ch_type].

    Returns:
        topo_2d_fig: matplotlib.image.AxesImage
            matplotlib image plot of a 2d topographic map based on the input epoch data
    """
    
    defaultKwargs = {'contours': 0, 'sphere': 100, 'res': 64, 'extrapolate': 'head', 'outlines': 'head',
                     'axes': None, 'mask': None, 'mask_params': None, 'image_interp': 'bilinear', 'show': False,
                     'onselect': None, 'border' : 'mean', 'ch_type': 'eeg'}
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
    
    if plotting_data is None:
        if isinstance(epoch, mne.epochs.Epochs):
            plotting_data = epoch.get_data()[0][:, recording_number]
        elif isinstance(epoch, mne.evoked.EvokedArray):
            plotting_data = epoch.data[:, recording_number]
    
    if type(plotting_data) == numpy.ndarray:
        if plotting_data.shape[0] != user_epoch.info['nchan']:
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
    
    
    if mark not in ['dot', 'r+', 'channel_name', 'none']:
        raise ValueError(
                """Passed mark is not accepted, please pass one of 'dot', 'r+',
                'channel_name', or 'none'"""
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

    if colorbar:
        fig, ax = plt.subplots()

    topo_2d_fig = mne.viz.plot_topomap(
        data=plotting_data,
        pos=epoch.info,  # Location info for data points
        vmin=cmin / 1e6,  # Convert back to volts
        vmax=cmax / 1e6,
        cmap=colormap, 
        sensors=sensor_value,  
        names=names_value, 
        show_names=show_names_value,
        **kwargs
    )[0]
    
    if timestamp:
        add_timestamp(epoch, recording_number, -130, 120)

    if colorbar:
        ax_divider = make_axes_locatable(ax)
        cax = ax_divider.append_axes("right", size=0.1, pad="0%")
        cmid = (cmin+cmax)/2
        clim = dict(kind='value', lims=[cmin, cmid, cmax])
        # https://mne.tools/stable/generated/mne.viz.plot_brain_colorbar.html
        mne.viz.plot_brain_colorbar(
            cax,
            clim,
            colormap=colormap,
            transparent=False,
            orientation='vertical',
            label='µV',
            bgcolor='0'
        )

    return topo_2d_fig


def animate_topomap_2d(epoch,
                       plotting_data=None,
                       colormap='RdBu_r',
                       mark='dot',
                       cmin=-30,
                       cmax = 30,
                       colorbar=True,
                       timestamp=True,
                       frame_rate=12,
                       **kwargs):
    """
    Plots a still image mne.epochs.Epochs EEG data as a 2D topomap using the mne.viz.plot_topomap
    function.

    Parameters:
        epochs: mne.epochs.Epochs
            MNE epochs object containing portions of raw EEG data built around specified timestamp(s)

        colormap: matplotlib colormap or None
            Specifies the 'colormap' parameter in the mne.viz.plot_topomap() function.

        mark: str
            Specifies what kind of marker should be shown for each node on the topomap. Can be one of
            'dot', 'r+' (for red +'s), 'channel_name', or 'none'.

        cmin: float
            Specifies the 'vmin' parameter in the mne.viz.plot_topomap() function.
            Sets the limits for the colors which will be used on the topomap. Value is
            in μV. Defaults to -10.
            
        cmax: float
            Specifies the 'vmax' parameter in the mne.viz.plot_topomap() function.
            Sets the limits for the colors which will be used on the topomap. Value is
            in μV. Defaults to +10.

        res: int
            Specifies the 'res' and parameters in the mne.viz.plot_topomap() function. "The
            resolution of the topomap image (n pixels along each side)."

        colorbar: bool
            Specifies whether or not to include a colorbar in the animation.
        
        timestamp: bool
            Specifies whether or not to show the timestamp on the plot relative to the time in the epoch that
            is being shown. Defaults to True.

        frame_rate: int
            The frame rate to genearte the final animation with.
        
        **kwargs: various
            Additional arguments from the 'mne.viz.plot_topomap' function
            (https://mne.tools/stable/generated/mne.viz.plot_topomap.html) may be provided. Since this function
            is used under the hood most of these arguments should work exactly as they do in their original
            function. The exact list of avalible arguments includes: [contours, sphere, res, extrapolate, outlines,
            mask, mask_params, image_interp, show, onselect, border, ch_type]. The 'axes' argument is not avalible
            since it does not work with animations.

    Returns:
        ani: matplotlib.animation.FuncAnimation
            matplotlib funcanimation of a 2d topographic map based on the input epoch data
    """
    
#     defaultKwargs = {'contours': 0, 'sphere': 100, 'res': 64, 'extrapolate': 'head', 'outlines': 'head',
#                     'mask': None, 'mask_params': None, 'image_interp': 'bilinear', 'show': False,
#                     'onselect': None, 'border' : 'mean', 'ch_type': 'eeg'}
#     kwargs = { **defaultKwargs, **kwargs }   

    # Generate array of all frames to be shown based on parameters
    # if epoch data is passed then extract a specific epoch number
    # and convert it to the same format as evoked data
    
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

    if type(plotting_data) == numpy.ndarray:
        frames_to_show = np.arange(0, plotting_data.shape[1], 1)
    elif isinstance(epoch, mne.epochs.Epochs):
        frames_to_show = np.arange(0, epoch.get_data()[0].shape[1], 1)
        plotting_data = epoch.get_data()[0]
    elif isinstance(epoch, mne.evoked.EvokedArray):
        frames_to_show = np.arange(0, evoked.data.shape[1], 1)
        plotting_data = epoch

    ms_between_frames = 1000 / frame_rate

    fig, ax = plt.subplots()
    
    if colorbar:
        ax_divider = make_axes_locatable(ax)
        cmid = (cmin+cmax)/2
        clim = dict(kind='value', lims=[cmin, cmid, cmax])
        

    def animate(frame_number):
        fig.clear()
        ax.clear()
        # https://mne.tools/dev/generated/mne.viz.plot_topomap.html
        topomap_2d = plot_topomap_2d(
            epoch=epoch,
            plotting_data=plotting_data[:, frame_number],
            colormap=colormap,
            mark=mark,
            cmin = cmin,
            cmax = cmax,
            timestamp = False,
            colorbar=False,
            **kwargs
        )
        
        if timestamp:
            add_timestamp(epoch, frame_number, -35, -130)

        if colorbar:
            cax = ax_divider.append_axes("right", size=0.1, pad="0%")
            # https://mne.tools/stable/generated/mne.viz.plot_brain_colorbar.html
            mne.viz.plot_brain_colorbar(
                cax,
                clim,
                colormap=colormap,
                transparent=False,
                orientation='vertical',
                label='µV',
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