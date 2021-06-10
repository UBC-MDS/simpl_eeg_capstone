import matplotlib.pyplot as plt
import matplotlib.animation as animation
import mne
import numpy as np
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable


def add_timestamp(epoch, frame_number, xpos, ypos):
    """
    Adds a timestamp to a matplotlib.image.AxesImage object
    
    Parameters
    ----------
    epoch : mne.epochs.Epochs
        MNE epochs object containing the timestamps.

    frame_number: int
        The timestamp to plot.
    
    xpos: float
        The matplotlib x coordinate of the timestamp.

    ypos: float
        The matplotlib y coordinate of the timestamp.
        
    Returns
    -------
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
                    contours=0,
                    sphere=100,
                    res=100,
                    extrapolate='head',
                    outlines='head',
                    axes=None,
                    mask=None,
                    mask_params=None,
                    timestamp = True,
                    ):
    """
    Plots a still image mne.epochs.Epochs EEG data as a 2D topomap using the mne.viz.plot_topomap
    function.

    Parameters
    ----------
    epoch : mne.epochs.Epochs
        MNE epochs object containing portions of raw EEG data built around specified timestamp(s)

    plotting_data: numpy.ndarray
        array of the EEG data from a measurement (not a time interval) to be plotted
    
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

    contours: int or array of float
        specifies the 'contours' parameter in the mne.viz.plot_topomap() function. "The number of
        contour lines to draw. If 0, no contours will be drawn. If an array, the values represent
        the levels for the contours. The values are in µV for EEG, fT for magnetometers and fT/m
        for gradiometers."

    sphere: float or array_like or instance of ConductorModel
        specifies the 'sphere' parameter in the mne.viz.plot_topomap() function. "The sphere
        parameters to use for the cartoon head. Can be array-like of shape (4,) to give the
        X/Y/Z origin and radius in meters, or a single float to give the radius (origin
        assumed 0, 0, 0). Can also be a spherical ConductorModel, which will use the origin
        and radius. Can also be None (default) which is an alias for 0.095"

    res: int
        Specifies the 'res' and parameters in the mne.viz.plot_topomap() function. "The
        resolution of the topomap image (n pixels along each side)."

    extrapolate: str
        Specifies the 'extrapolate' and parameters in the mne.viz.plot_topomap() function. One of
        "box", "local", or "head".

    outlines: ‘head’ or ‘skirt’ or dict or None
        Specifies the 'outlines' parameter in the mne.viz.plot_topomap() function.

    axes: instance of Axes or None
        Specifies the 'axes' parameter in the mne.viz.plot_topomap() function.

    mask: ndarray of bool, shape (n_channels, n_times) or None
        Specifies the 'mask' parameter in the mne.viz.plot_topomap() function.

    mask_params: dict
        Specifies the 'mask_params' parameter in the mne.viz.plot_topomap() function.
        
    timestamp: bool
        Specifies whether or not to show the timestamp on the plot relative to the time in the epoch that
        is being shown. Defaults to true.

    Returns
    -------
    topo_2d_fig: matplotlib.image.AxesImage
        matplotlib image plot of a 2d topographic map based on the input epoch data
    """

    # Need to decide whether to keep plotting_data as a parameter or not

    if not isinstance(plotting_data, np.ndarray):
        if isinstance(epoch, mne.epochs.Epochs):
            plotting_data = epoch.get_data()[
                0][:, recording_number]
        elif isinstance(epoch, mne.evoked.EvokedArray):
            plotting_data = epoch.data[:, recording_number]

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
        show=False,
        vmin=cmin / 1e6,  # Convert back to volts
        vmax=cmax / 1e6,
        sphere=sphere,  # Causes head to appear, see documentation, not sure what value should be here so 100 is placeholder
        outlines=outlines,
        # 'head' keeps signals within head space, 'skirt' extrapolates beyond
        extrapolate=extrapolate,  # 'local' is off-center
        res=res,  # n x n pixels in the actual waves 
        cmap=colormap, 
        sensors=sensor_value,  # True=black dots, "r+"=red + 
        axes=None,  # used if you're plotting multiple images 
        names=names_value,  # Feed in channel names
        show_names=show_names_value,  # Show channel names at each location 
        mask=mask,  # Marks siginficant points/times if that's wanted
        mask_params=None,  
        contours=contours,  # Number of lines that divide up sections to be drawn
    )[0]
    
    if timestamp:
        add_timestamp(epoch, recording_number, -130, 120)

    if colorbar:
        ax_divider = make_axes_locatable(ax)
        cax = ax_divider.append_axes("right", size="3%", pad="0%")
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
                       colormap='RdBu_r',
                       mark='dot',
                       contours=0,
                       sphere=100,
                       cmin=-30,
                       cmax = 30,
                       res=100,
                       extrapolate='head',
                       outlines='head',
                       axes=None,
                       mask=None,
                       mask_params=None,
                       colorbar=True,
                       timestamp = True,
                       frame_rate=12):
    """
    Plots a still image mne.epochs.Epochs EEG data as a 2D topomap using the mne.viz.plot_topomap
    function.

    Parameters
    ----------
    epochs : mne.epochs.Epochs
        MNE epochs object containing portions of raw EEG data built around specified timestamp(s)

    colormap: matplotlib colormap or None
        Specifies the 'colormap' parameter in the mne.viz.plot_topomap() function.

    mark: str
        Specifies what kind of marker should be shown for each node on the topomap. Can be one of
        'dot', 'r+' (for red +'s), 'channel_name', or 'none'.

    contours: int or array of float
        specifies the 'contours' parameter in the mne.viz.plot_topomap() function. "The number of
        contour lines to draw. If 0, no contours will be drawn. If an array, the values represent
        the levels for the contours. The values are in µV for EEG, fT for magnetometers and fT/m
        for gradiometers."

    sphere: float or array_like or instance of ConductorModel
        specifies the 'sphere' parameter in the mne.viz.plot_topomap() function. "The sphere
        parameters to use for the cartoon head. Can be array-like of shape (4,) to give the
        X/Y/Z origin and radius in meters, or a single float to give the radius (origin
        assumed 0, 0, 0). Can also be a spherical ConductorModel, which will use the origin
        and radius. Can also be None (default) which is an alias for 0.095"

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

    extrapolate: str
        Specifies the 'extrapolate' and parameters in the mne.viz.plot_topomap() function. One of
        "box", "local", or "head".

    outlines: ‘head’ or ‘skirt’ or dict or None
        Specifies the 'outlines' parameter in the mne.viz.plot_topomap() function.

    axes: instance of Axes or None
        Specifies the 'axes' parameter in the mne.viz.plot_topomap() function.

    mask: ndarray of bool, shape (n_channels, n_times) or None
        Specifies the 'mask' parameter in the mne.viz.plot_topomap() function.

    mask_params: dict
        Specifies the 'mask_params' parameter in the mne.viz.plot_topomap() function.

    colorbar: bool
        Specifies whether or not to include a colorbar in the animation.
    
    timestamp: bool
        Specifies whether or not to show the timestamp on the plot relative to the time in the epoch that
        is being shown. Defaults to True.

    frame_rate: int
        The frame rate to genearte the final animation with.

    Returns
    -------
    ani: matplotlib.animation.FuncAnimation
        matplotlib funcanimation of a 2d topographic map based on the input epoch data
    """

    # Generate array of all frames to be shown based on parameters
    # if epoch data is passed then extract a specific epoch number
    # and convert it to the same format as evoked data

    if isinstance(epoch, mne.epochs.Epochs):
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
            contours=contours,
            sphere=sphere,
            colorbar=False,
            cmin = cmin,
            cmax = cmax,
            res=res,
            extrapolate=extrapolate,
            outlines=outlines,
            axes=axes,
            mask=mask,
            mask_params=mask_params,
            timestamp = False
        )
        
        if timestamp:
            add_timestamp(epoch, frame_number, -35, -130)
        
        topomap_2d = plt.plot(1,2)

        if colorbar:
            cax = ax_divider.append_axes("right", size="3%", pad="0%")
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
