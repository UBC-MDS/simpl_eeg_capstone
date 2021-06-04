import matplotlib.pyplot as plt
import matplotlib.animation as animation
import mne
import numpy as np
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable


def plot_topomap_2d(epochs,
                    plotting_data=None,
                    epoch_number=0,
                    recording_number=0,
                    colormap='RdBu_r',
                    colorbar=True,
                    cmin = -30, 
                    cmax = 30,
                    mark='dot',
                    contours='6',
                    sphere=100,
                    res=100,
                    extrapolate='head',
                    outlines='head',
                    axes=None,
                    mask=None,
                    mask_params=None,
                    ):
    """
    Plots a still image mne.epochs.Epochs EEG data as a 2D topomap using the mne.viz.plot_topomap
    function.

    Parameters
    ----------
    epochs : mne.epochs.Epochs
        MNE epochs object containing portions of raw EEG data built around specified timestamp(s)

    plotting_data: numpy.ndarray
        array of the EEG data from a measurement (not a time interval) to be plotted

    epoch_number: int
        The epoch in the epochs data to plot.
    
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

    Returns
    -------
    topo_2d_fig: matplotlib.image.AxesImage
        matplotlib image plot of a 2d topographic map based on the input epoch data
    """

    # Need to decide whether to keep plotting_data as a parameter or not

    if not isinstance(plotting_data, np.ndarray):
        if isinstance(epochs, mne.epochs.Epochs):
            plotting_data = epochs[epoch_number].get_data()[
                0][:, recording_number]
        elif isinstance(epochs, mne.evoked.EvokedArray):
            plotting_data = epochs.data[:, recording_number]

    names_value = False
    sensor_value = True
    show_names_value = False

    if mark == 'r+':
        sensor_value = 'r+'
    if mark == 'channel_name':
        names_value = epochs.ch_names
        show_names_value = True
    if mark == 'none':
        sensor_value = False

    if colorbar:
        fig, ax = plt.subplots()

    topo_2d_fig = mne.viz.plot_topomap(
        data=plotting_data,
        pos=epochs.info,  # Location info for data points
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


def animate_topomap_2d(epochs,
                       colormap='RdBu_r',
                       epoch_number=0,
                       mark='dot',
                       contours='6',
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

    if isinstance(epochs, mne.epochs.Epochs):
        frames_to_show = np.arange(0, epochs[0].get_data()[0].shape[1], 1)
        plotting_data = epochs[epoch_number].get_data()[0]
    elif isinstance(epochs, mne.evoked.EvokedArray):
        frames_to_show = np.arange(0, evoked.data.shape[1], 1)
        plotting_data = epochs

    ms_between_frames = 1000 / frame_rate

    if colorbar:
        fig, ax = plt.subplots()
        ax_divider = make_axes_locatable(ax)
        
        cmid = (cmin+cmax)/2
        
        clim = dict(kind='value', lims=[cmin, cmid, cmax])

    def animate(frame_number):
        fig.clear()
        # https://mne.tools/dev/generated/mne.viz.plot_topomap.html
        topomap_2d = plot_topomap_2d(
            epochs=epochs,
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
            mask_params=mask_params
        )

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
        interval=ms_between_frames,  # Time between frames in ms
        blit=True
    )

    return ani
