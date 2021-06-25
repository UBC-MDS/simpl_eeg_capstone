import os
import os.path as op
import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mne.datasets import fetch_fsaverage
from mne.minimum_norm import make_inverse_operator
from mne.minimum_norm import apply_inverse_epochs
from mne.minimum_norm import apply_inverse
import matplotlib.gridspec as gridspec
from matplotlib.transforms import Bbox
import matplotlib.animation as animation

def add_timestamp_brain(stc, figure, frame_number, xpos, ypos, fontsize):
    """
    Adds a timestamp to a matplotlib.image.AxesImage object

    Parameters:
        stc: mne.source_estimate.SourceEstimate
            The stc to get proper timestamps from.
    
        figure: matplotlib.figure.Figure
            The time to plot as a timestamp.

        frame_number: int
            The frame_number of the stc to plot as a timestamp.

        xpos: float
            The matplotlib x coordinate to place the timestamp.
            
        ypos: float
            The matplotlib y coordinate to place the timestamp.

        fontsize:
            The size to generate the font.
    """
    frame_time = stc.times[frame_number]
    tstamp = format(frame_time, '.4f')
    if float(frame_time) >= 0:
        time_str = 'time:  {}'.format(tstamp) + 's'
    else:
        time_str = 'time: {}'.format(tstamp) + 's'
        
    figure.text(xpos,
                ypos,
                time_str,
                fontsize=fontsize,
                color = 'white',
                clip_on=True)


def calculate_cbar_dims(img_width, img_figsize, img_height):
    """
    Helper for plot_topomap_3d_brain when plotting multiple views and using the
    matplotlib backend. Calculates the colorbar width and height to be placed
    correctly.

    Parameters:
        img_width: matplotlib.figure.Figure
            Number of brain images to include horizontally.
        img_figsize: int
            Total height/width of the image in inches (square image).
        img_height: int
            Number of brain images to include vertically.

    Returns:
        cbar_width: float
            Width of colorbar in matplotlib units.
        cbar_height: float
            Height of colorbar in matplotlib units.
    """
    cbar_adjustments_table = {1: [1.365, 1.43],
                              2: [0.689, 0.71],
                              3: [0.611, 0.57],
                              4: [0.559, 0.50],
                              5: [0.494, 0.45],
                              6: [0.455, 0.40],
                              7: [0.429, 0.38]}
    cbar_adjustments = cbar_adjustments_table[img_width]
    
    cbar_height = img_figsize * img_width * cbar_adjustments[0]
    cbar_width = img_figsize * img_width * cbar_adjustments[1]
    
    return cbar_width, cbar_height

def convert_figure_to_image(fig, img_height, img_width):
    """
    Helper for animate_matplot_brain. Converts figure to image when plotting multiple
    views and then cuts out the empty space. This must be done when animating to
    preserve the figure dimensions as they otherwise get cut-off.

    Parameters:
        fig: matplotlib.figure.Figure
            Matplotlib figure to convert to image.
        img_height: int
            Number of brain images to include vertically.
        img_width: matplotlib.figure.Figure
            Number of brain images to include horizontally.

    Returns:
        plot_image: numpy.ndarray
            Image built from figure that will be animated.
    """

    fig.canvas.draw()
    plot_image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    plot_image = plot_image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    cropped_height = round(plot_image.shape[0] * (img_height / img_width))
    cropped_height = plot_image.shape[1] - cropped_height

    if img_width == 1:
        plot_image = plot_image[cropped_height:, 0:round(plot_image.shape[1]*0.5), :]
    else:
        plot_image = plot_image[cropped_height:, :, :]
    
    print("type of plot image is" + str(type(plot_image)))
    
    return plot_image


def move_axes(ax, fig, copy = False):
    """
    Moves or copies axes from one matplotlib.figure.Figure to another.

    Parameters:
        ax: matplotlib.axes._subplots.AxesSubplot
            Matplotlib axis that will be moved to a new figure.

        fig: matplotlib.figure.Figure
            Matplotlib figure the axis will be moved to.

    Returns:
    """
    # get a reference to the old figure context so we can release it
    old_fig = ax.figure

    # remove the Axes from it's original Figure context
    if copy == False:
        ax.remove()
    ax.figure = fig

    # add the Axes to the registry of axes for the figure
    fig.axes.append(ax)
    fig.add_axes(ax)

def calculate_clim_values(cmin, cmid, cmax, colormap_limit_type):
    """
    Creates clim_values to be used in colorbar/figure generation

    Parameters:
        ax: matplotlib.axes._subplots.AxesSubplot
            Matplotlib axis that will be moved to a new figure.

        fig: matplotlib.figure.Figure
            Matplotlib figure the axis will be moved to.

    Returns:
    """
    if (cmin is None) and (cmax is None):
        clim_values = 'auto'
    else:
        if cmin is None:
            cmin = -cmax
        if cmax is None:
            cmax = -cmin
        if cmid is None:
            cmid = (cmin + cmax) / 2

        if colormap_limit_type == 'lims':
            clim_values = dict(kind='value', lims=[
                cmin,
                cmid,
                cmax]
            )
        elif colormap_limit_type == 'pos_lims':
            clim_values = dict(kind='value', pos_lims=[
                cmin,
                cmid,
                cmax]
            )
    return clim_values

def create_fsaverage_forward(epoch, **kwargs):
    """
    A forward model is an estimation of the potential or field distribution for a known source
    and for a known model of the head. Returns EEG forward operator with a downloaded template
    MRI (fsaverage).

    Parameters:
        epoch: mne.epochs.Epochs
                MNE epoch object containing portions of raw EEG data built around specified timestamp(s).

        kwargs: arguments
                Specify any of the following arguments for the mne.make_forward_solution() function. These include midist=5.0, n_jobs=1.

    Returns:
        mne.forward.forward.Forward:
            Forward operator built from the user_input epoch and the fsaverage brain.
    """

    defaultKwargs = { 'n_jobs': 1, 'mindist': 5.0 }
    kwargs = { **defaultKwargs, **kwargs }

    # Download fsaverage files
    fs_dir = fetch_fsaverage(verbose=True)
    subjects_dir = op.dirname(fs_dir)

    # Used to download/load example MRI brain model
    # The files live in:
    subject = 'fsaverage'
    trans = 'fsaverage'  # MNE has a built-in fsaverage transformation
    src = op.join(fs_dir, 'bem', 'fsaverage-ico-5-src.fif')
    bem = op.join(fs_dir, 'bem', 'fsaverage-5120-5120-5120-bem-sol.fif')

    fwd = mne.make_forward_solution(epoch.info,
                                    trans=trans,
                                    src=src,
                                    bem=bem,
                                    eeg=True,
                                    **kwargs)

    return fwd


def create_inverse_solution(
        epoch,
        fwd,
        covariance_method=[
            'empirical',
            'shrunk'],
        apply_inverse_method="dSPM",
        loose=0.2,
        depth=0.8,
        snr=3.0,
        pick_ori='normal'):
    """
    Calculates the inverse solution, which is an Estimation of the unknown sources
    corresponding to the measured EEG or MEG.

    Parameters:
        epoch: mne.epochs.Epochs or mne.evoked.EvokedArray
            MNE epochs or evoked object containing portions of raw EEG data built around specified
            timestamp(s). The inverse solution will be built based on the data in the specified epoch.

        fwd: mne.forward.forward.Forward
            Specifies the 'forward' parameter in the mne.minimum_norm.make_inverse_operator() function.

        epoch_num: int or 'all'
            If input is an 'int' then this specifies which epoch in the 'epochs' number to build an
            inverse solution from. If input is "all" then an inverse solution will be built from all
            epochs.

        covariance_method: list
            Specifies the 'method' parameter in the mne.compute_covariance() function.

        loose: float
            Specifies the 'loose' parameter in the mne.minimum_norm.make_inverse_operator() function.

        depth: float
            Specifies the 'depth' parameter in the mne.minimum_norm.make_inverse_operator() function.

        snr: float
            Used to calculate 'lambda2' in the equation 'lambda2 = 1.0 / snr ** 2'.

        inverse_epochs_method: str
            Specifies the 'method' parameter in mne.minimum_norm.apply_inverse_epochs() (if using epochs)
            or mne.minimum_norm.apply_inverse() (if using evoked data).

        pick_ori: str
            Specifies the 'pick_ori' parameter in mne.minimum_norm.apply_inverse_epochs() (if using epochs)
            or mne.minimum_norm.apply_inverse() (if using evoked data).

    Returns:
        mne.source_estimate.SourceEstimate:
            Forward operator built from the user_input epochs and the fsaverage brain.
    """

    if type(epoch) == mne.epochs.Epochs:
        if len(epoch.events) > 1:
            raise Warning(
                """Epoch with multiple events passed. The first event will be used to
                generate the STC. If you wish to see a specific event_number please pass
                epoch[event_number]. If you wish to see an averaged version of all of
                your epochs please pass evoked data instead (generated using 
                `evoked = epoch.average()`)"""
            )

    noise_cov = mne.compute_covariance(epoch, method=covariance_method)

    inverse_operator = make_inverse_operator(epoch.info, fwd, noise_cov,
                                             loose=loose, depth=depth)

    lambda2 = 1.0 / snr ** 2

    # If epoch_num is any string other than "all" return false

    if isinstance(epoch, mne.epochs.Epochs):
        stc = apply_inverse_epochs(epoch,
                                   inverse_operator=inverse_operator,
                                   lambda2=lambda2,
                                   method=apply_inverse_method,
                                   pick_ori=pick_ori)
        stc = stc[0]

    elif isinstance(epoch, mne.evoked.EvokedArray):
        stc = apply_inverse(epoch,
                            inverse_operator=inverse_operator,
                            lambda2=lambda2,
                            method=apply_inverse_method,
                            pick_ori=pick_ori)

    return stc

def create_inverse_solution_auto(stc = 'auto', fwd = 'auto', epoch = None):
    # Calculate stc/forward they are not provided in plotting function
    gen_stc = None
    if stc == 'auto' and fwd == 'auto' and epoch != None:
        gen_forward = create_fsaverage_forward(epoch)
        gen_stc = create_inverse_solution(epoch, gen_forward)
    elif stc == 'auto' and fwd != 'auto' and epoch != None:
        gen_stc = create_inverse_solution(epoch, fwd)
    elif stc != 'auto' and fwd != 'auto' and epoch != None:
        raise Warning("""Forward, epoch, and stc have been provided.
                         The plot has been generated from the stc only,
                         and the forward/epoch was not be used.""")
    elif stc != 'auto' and fwd == 'auto' and epoch != None:
        raise Warning("""Epoch and stc have both been provided.
                         The plot has been generated from the stc only,
                         and the epoch was not be used.""")
    elif stc != 'auto' and fwd != 'auto' and epoch == None:
        raise Warning("""stc and fwd have both been provided.
                         The plot has beengenerated from the stc only,
                         and the fwd was not used.""")
    
    if gen_stc == None:
        return stc
    else:
        return gen_stc


def plot_topomap_3d_brain(
        epoch=None,
        fwd='auto',
        stc='auto',
        recording_number=0,
        backend='matplotlib',
        views=[
            'lat',
            'fro',
            'dor'],
        view_layout='horizontal',
        size=300,
        hemi='both',
        colormap='mne',
        colormap_limit_type='lims',
        cmin=None,
        cmid=None,
        cmax=None,
        colorbar=True,
        time_viewer = 'auto',
        background='black',
        foreground='white',
        spacing='oct6',
        smoothing_steps=3,
        timestamp=True,
        figure=None,
        **kwargs):
    """
    Creates a still image figure of the epochs or stc data mapped to the brain using the 
    mne.SourceEstimate.plot function. Generates when provided with 1. an stc (see
    create_inverse_solution) (FASTEST) 2. an epoch and acommpanying fwd (see
    create_fsaverage_forward) (reccomended) 3. an epoch on its own (SLOWEST). This function 
    is written to work with either a 'pyvista' or 'matplotlib' backend. Note pyvista and mayavi
    backend dependencies must be installed independently of the simpl_eeg package (see 
    `topo_3d_brain` in instructions for details) if you wish to use their backends.

    Parameters:
        epoch: mne.epochs.Epoch or None
            MNE epochs object containing portions of raw EEG data built around specified
            timestamp(s). If no fwd and stc are provided a fwd will be generated from the
            epoch using create_fsaverage_forward(). The epoch and fwd (either provided or
            generated) will then be used in create_inverse_solution() to generate an stc that
            the brain figure will be generated from.
        
        fwd: mne.forward.forward.Forward or 'auto'
            MNE forward object. If provided alongside an epoch they will both be used in
            create_fsaverage_forward() to create an stc which the brain figure will then be
            generated from. Defaults to 'auto'.

        stc: mne.source_estimate.SourceEstimate or 'auto'
            'inverse_solution' to generate the plot from. If set to "auto" then an stc will be
            automatically generated from either an epoch or an epoch and a fwd, however, this
            will significantly slow down rendering time. Defaults to 'auto'.

        recording_number: int or None
            Specifies the recording number in the epoch/stc to render. Defaults to 0 (the first frame).

        backend: str (‘auto’ or ‘mayavi’ or ‘pyvista’ or ‘matplotlib’)
            Specifies the 'initial_time' parameter in the mne.SourceEstimate.plot() function. "If 'auto', 
            tries to plot with pyvista, but resorts to matplotlib if no 3d backend is available."
            Note that 'mayavi' has not been tested for this function. Using matplotlib as a backend will lead to
            some functionality breaking (look at the documentation on a function-by-function basis to know which
            to avoide). Note pyvista and mayavi backend dependencies must be installed independently of the
            simpl_eeg package (see `topo_3d_brain` in instructions for details) if you wish to use those backends.
            Defaults to 'matplotlib'.

        views: str or list
            Specifies the 'view' parameter in the mne.SourceEstimate.plot() function. For any backend
            can be any combination of 'lat' (lateral), 'med' (medial), 'ros' (rostral), 'cau' (caudal),
            'dor' (dorsal), 'ven'(ventral), 'fro'(frontal), 'par' (parietal). The following arguments
            are also accepted but are NOT compatible with the matplotlib backend 'axi' (axial), 'sag'
            (sagittal), and 'cor'(coronal). Defaults to ['lat', 'fro', 'dor'].

        view_layout: str
            Specifies the 'view_layout' parameter in the mne.SourceEstimate.plot() function. Should be
            'vertical' or 'horizontal'. Using 'horizontal' with hemi set to 'split' might cause issues.
            NOTE that this argument has no effect when using the 'matplotlib' backend. Defaults to 'horizontal'.

        size: int
            If using a non-matplotlib backend then specifies how many pixels tall EACH "view" of the brian will be.
            If using matplotlib as a backend then the height will be divided by 100 and rounded the closest inch.
            For example, entering 100 will result in 1 inch per view. If plotting multiple views overall size of
            the multiplot is automatically calculated to fit all views. Defaults to 300.         

        hemi: str ('lh’ or ‘rh’ or ‘both’ or ‘split’)
            Specifies the 'initial_time' parameter in the mne.SourceEstimate.plot() function. Can be
            one of ‘lh’, ‘rh’, ‘both’, or ‘split’. Defaults to 'both'. Note that when using the matplotlib
            backend that 'split' and 'both' will return a 'split' view since both is not avalible.
            Defaults to 'both'.

        colormap: str or np.ndarray of float, shape(n_colors, 3 | 4)
            Specifies the 'colormap' parameter in the mne.SourceEstimate.plot() function. Can use a
            matplotlib colormap by name or take a custom look up table as input. Defaults to "mne" since
            this colormap provides a grey texture for the brain.

        colormap_limit_type: str
            Can be either "lims" or "pos_lims". "lims" means that your cmin, cmid, and cmax values will specify the
            "Lower, middle, and upper bounds for colormap". Using "pos_lims" will lead to cmin, cmid, and cmax representing
            the "Lower, middle, and upper bound for colormap. Positive values will be mirrored directly across
            zero during colormap construction to obtain negative control points." Defaults to "lims".

        cmin: float
            Specifies the lower value of the colormap limit. If no value is specified then
            limits will be automatically calculated based on the mne.SourceEstimate.plot() function defaults OR
            will be the negative value of cmax if only that is provided.

        cmid: float
            Specifies the middle value of the colormap limit. If no value is specified then
            limits will be automatically calculated based on the mne.SourceEstimate.plot() function defaults OR
            will be the value between cmin and cmax if one/both of them is provided.

        cmax: float
            Specifies the middle value of the colormap limit. If no value is specified then
            limits will be automatically calculated based on the mne.SourceEstimate.plot() function defaults OR
            will be the negative value of cmin if only that is provided.

        colorbar: bool
            Determines whether to include a colorbar on the plot not. Defaults to True.

        time_viewer: bool or str
            Specifies the 'time_viewer' parameter in the mne.SourceEstimate.plot() function. 'auto' by default. With a
            PyVista backend this will allow for the user to interact with the genreated plot. Has no effect on figures
            generated with the matplotlib backend. 

        background: matplotlib color
            Specifies the 'background' parameter in the mne.SourceEstimate.plot() function. Does not work with plots
            made with the matplotlib backend. 'black' by default.

        foreground: matplotlib color
            Specifies the 'foreground' parameter in the mne.SourceEstimate.plot() function. Does not work with plots
            made with the matplotlib backend. 'white' by default.

        spacing: str
            Specifies the 'spacing' parameter in the mne.SourceEstimate.plot() function. "The spacing to use for the
            source space. Can be 'ico#' for a recursively subdivided icosahedron, 'oct#' for a recursively subdivided
            octahedron. In general, you can speed up the plotting by selecting a sparser source
            space. Has no effect with mayavi backend. Defaults to ‘oct6’".

        smoothing_steps: int
            Specifies the 'smoothing_steps' parameter in the mne.SourceEstimate.plot() function. "The amount of smoothing".
            3 by default.
        
        timestamp: bool
            Specifies whether or not to show the timestamp on the plot relative to the time in the epoch that
            is being shown. Defaults to True.

        figure: instance of mayavi.core.api.Scene or instance of matplotlib.figure.Figure or list or int or None
            Specifies the 'figure' parameter in the mne.SourceEstimate.plot() function. "If None, a new figure
            will be created. If multiple views or a split view is requested, this must be a list of the appropriate
            length. If int is provided it will be used to identify the Mayavi figure by it’s id or create a new figure
            with the given id. If an instance of matplotlib figure, mpl backend is used for plotting." NOTE that if plotting
            multiple views OR a split/both hemi with the matplotlib backend then this argument will not work. None by default.

    Returns:
        matplotlib.figure.Figure or mne.viz.figure
            If using 'matplotlib' backend (default) then returns a matplotlib.figure.Figure. If using 'pyvista'
            then returns a mne.viz.figure of brain with input epoch or stc data mapped to it. 
    """

    defaultKwargs = {'transparent': False, 'alpha': 1.0, 'surface': 'inflated', 'cortex': 'classic',
                     'subject': None, 'time_label': 'auto', 'time_unit': 's', 'volume_options': None,
                     'subjects_dir': None, 'title': None, 'show_traces': 'auto', 'src': None, 'verbose': None }
    kwargs = { **defaultKwargs, **kwargs }    
    
    if type(epoch) is not mne.epochs.Epochs and type(epoch) is not mne.evoked.EvokedArray and epoch is not None:
        raise TypeError(
            """Passed epoch object is not in the correct format, 
            please pass an mne.epochs.Epochs object or None instead"""
        )
    
    if type(fwd) is not mne.forward.forward.Forward and fwd != 'auto':
        raise TypeError(
            """Passed fwd object is not in the correct format, 
            please pass an mne.forward.forward.Forward object or "auto" instead"""
        )
    
    if type(stc) is not mne.source_estimate.SourceEstimate and stc != 'auto':
        raise TypeError(
            """Passed stc object is not in the correct format, 
            please pass an mne.source_estimate.SourceEstimate object or 'auto' instead"""
        )
    
    if type(fwd) is mne.forward.forward.Forward and stc != 'auto' and epoch == None:
        raise TypeError(
            """Only a fwd object was passed, please pass either a fwd and an epoch OR 
            only an stc instead"""
        )
    
    
    if isinstance(recording_number, (int, np.integer)) == False:
        raise TypeError(
                """Passed recording_number object is not in the correct format, 
                please pass an int object instead"""
            )
    #print(type(recording_number))
    
    if backend not in ['auto', 'mayavi', 'pyvista', 'matplotlib']:
        raise ValueError(
                """Passed backend is not accepted, please pass one of "auto",
                "pyvista", "matplotlib", or "mayavi" instead"""
            )
        
    views_error = """please pass a str or list containing any cobination of 'lat'
                (lateral), 'med' (medial), 'ros' (rostral), 'cau' (caudal),
                'dor' (dorsal), 'ven'(ventral), 'fro'(frontal), or 'par' (parietal). The following arguments
                are also accepted but are NOT compatible with the matplotlib backend 'axi' (axial), 'sag'
                (sagittal), and 'cor'(coronal)."""
    
    if type(views) != str and type(views) != list:
        raise TypeError(
                """Passed views object is not in the correct format, """ + views_error
            )
    
    matplot_views = ['lat', 'med', 'ros', 'cau', 'dor', 'ven', 'fro', 'par']
    non_matplot_views = matplot_views + ['axi', 'sag', 'cor']
    
    if type(views) == str:
        if views not in non_matplot_views:
            raise ValueError("""Passed view is not accepted,""" + views_error)
        if backend == 'matplotlib' and views not in matplot_views:
            raise ValueError("""Passed view is not accepted,""" + views_error)
    
    if type(views) == list:
        if all(e in non_matplot_views for e in views) == False:
            raise ValueError("""At least one of the passed views is not accepted,""" + views_error)
        if backend == 'matplotlib' and all(e in matplot_views for e in views) == False:
            raise ValueError("""At least one of the passed views is not accepted,""" + views_error)
    
    if view_layout not in ['vertical', 'horizontal']:
        raise ValueError(
                """Passed view_layout is not accepted, please pass one of 'horizontal' or 
                'vertical'."""
            )
    
    if type(size) is not int:
            raise TypeError(
                """Size value must be passed as an int"""
            )
    
    if hemi not in ['lh', 'rh', 'both', 'split']:
        raise ValueError(
                """Passed hemi is not accepted, please pass one of "lh" (left hemisphere), "rh" (right
                hemisphere), "both" (both hemispheres), "split" (split hemisphere view)"""
            )
    
    if type(colorbar) is not bool:
            raise TypeError(
                """Colorbar value must be a bool (True or False)"""
            )
    
    if colormap_limit_type not in ['lims', 'pos_lims']:
            raise ValueError(
                """Passed colormap_limit_type is not accepted, please pass one of 'lims' or 
                'pos_lims'."""
            )
            
    if type(timestamp) is not bool:
        raise TypeError(
            """Passed timestamp object is not in the correct format, 
            please pass a bool (True/False) instead"""
        )

    # Calculate stc if it is not provided
    gen_stc = create_inverse_solution_auto(stc = stc, fwd = fwd, epoch = epoch)
    plot_stc = gen_stc.copy()

    # Prep properties of the figure if not using a matplotlib backend
    if backend != 'matplotlib':
        # Calculate font size for colorbar/time label
        colorbar_font_size = round(size / 25)
        time_label_size = round(size / 33)

        # add 4/3 of the height in width for each visual
        if view_layout == "horizontal":
            auto_plot_size = [
                round(len(views) * (size * 4 / 3)), size]
        elif view_layout == "vertical":
            auto_plot_size = [round(size * 4/3),size *len(views)]

    # Preparation for if a matplotlib backend is being used then 
    else: 
        img_figsize = round(size / 100)
        if isinstance(views, str):
            views = [views]
        
        # Crop stc to only a recording since there are no user controls
        plot_stc.crop(plot_stc.times[recording_number], plot_stc.times[recording_number])
        
        # Layout MUST be horizontal and foreground/background colors cannot be changed
        # and auto_plot_size, colorbar_font_size, time_label_size inputs do nothing
        view_layout == "horizontal"
        background='black'
        foreground = 'white'
        auto_plot_size = None
        colorbar_font_size = None
        time_label_size = None

    # Set colorbar values
    clim_values = calculate_clim_values(cmin, cmid, cmax, colormap_limit_type)

    def make_plot(
        views=views,
        hemi=hemi,
        size=auto_plot_size,
        colorbar = colorbar,
        figure=figure
    ):
        plt.show(block=True)
        brain = plot_stc.plot(
            views=views,
            hemi=hemi,
            colormap=colormap,
            size=size,
            clim=clim_values,
            colorbar=colorbar,
            figure=figure,
            background=background,
            foreground=foreground,
            backend=backend,
            view_layout=view_layout,
            spacing = spacing,
            smoothing_steps=smoothing_steps,
            brain_kwargs=dict(
                show=False),
            add_data_kwargs=dict(
                time_label_size=time_label_size,
                colorbar_kwargs=dict(
                    label_font_size=colorbar_font_size)),
            **kwargs
        )
        return brain
    
    
    if backend != 'matplotlib':
        return (make_plot())

    elif (hemi == 'lh' and len(views) == 1) or (hemi == 'rh' and len(views) == 1):
        
        brain = make_plot(views=views[0])
        
        if colorbar == False:
            brain.axes[1].remove()
        
        if timestamp:
            add_timestamp_brain(gen_stc, brain, recording_number, 0.18, 0.94, 15)

        return (brain)

    else:
        if hemi == 'both' or hemi == 'split':
            brain_hemi = ['lh', 'rh']
        else:
            brain_hemi = [hemi]

        img_width = len(views)
        img_height = len(brain_hemi)
        
        if img_width == 1:
            fig_dims = img_height * img_figsize
        else:
            fig_dims = img_width * img_figsize

        base_fig, ax = plt.subplots(
            figsize=(fig_dims, fig_dims), facecolor="black")
        plt.axis('off')

        # Set flag to generate colorbar later (adding it early causes bad scaling)
        add_colorbar = False
        if colorbar:
            colorbar = False
            add_colorbar = True

        # Run to add new fig for each view
        fig_x_pos = 0
        axes_pos = 1
        for v in range(len(views)):

            fig_y_pos = 0

            # run twice for each side of the brain if using both or split
            for h in range(len(brain_hemi)):

                plt.show(block=True)
                fig = plt.figure(figsize=(img_figsize, img_figsize))
                make_plot(
                    figure=fig,
                    hemi=brain_hemi[h],
                    views=str(views[v]),
                    colorbar=colorbar)

                # Move over the brain image only
                move_axes(fig.axes[0], base_fig, copy = False)

                # Reposition copied over figure to fit properly
                pos1 = base_fig.axes[1].get_position()
                pos2 = [
                    pos1.x0 + fig_x_pos,
                    pos1.y0 + fig_y_pos,
                    pos1.width,
                    pos1.height
                ]
                base_fig.axes[axes_pos].set_position(pos2)

                # Increment axes index and reset y positioning index
                axes_pos += 1
                fig_y_pos = 1

            fig_x_pos += 1

        # Generate dummy colorbar to move to the main figure
        if add_colorbar:
            
            cbar_width, cbar_height = calculate_cbar_dims(img_width, img_figsize, img_height)

            dummy_fig = plt.figure(figsize=(cbar_width, cbar_height))
            make_plot(figure=dummy_fig, hemi='lh', views='fro', colorbar=True)
            move_axes(dummy_fig.axes[1], base_fig)

            pos2 = [pos1.x0 + 0, pos1.y0 + 1, pos1.width, pos1.height]
            base_fig.axes[axes_pos].set_position(pos2)
        
        if timestamp:
                if img_height == 2 and img_width == 1:
                    xpos = 0.1
                    ypos = 0.48
                else:
                    ypos = 0
                    xpos = 0.7
                    for i in range(img_width-2):
                        if img_width >= 3:
                            xpos += 0.1/(2**(i))
                
                add_timestamp_brain(gen_stc, base_fig, recording_number, xpos-0.01, ypos, 6*img_figsize)
            
        # Adjust figure dimensions to fit everything
        base_fig.subplots_adjust(top=0.1, bottom=0, right=0.1, left=0,
                                 hspace=0, wspace=0)
        
    return(base_fig)


def save_animated_topomap_3d_brain(
        brain,
        filename,
        time_dilation=20,
        interpolation='linear',
        framerate=12,
        time_viewer=True):
    """
    Saves an animated mne.viz._brain._brain.Brain object as a gif using the mne.viz.Brain.save_movie()
    function. Saves animation of the entire figure.

    Parameters:
        brain: mne.viz._brain._brain.Brain
            mne.viz figure of brain which will be saved as a gif.

        filename: str
            'filename' parameter in mne.viz.Brain.save_movie() function. "Path at which to save the movie.
            The extension determines the format (e.g., '*.mov', '*.gif', …; see the imageio documentation
            for available formats)".

        time_dilation: float
            'time_dilation' parameter in mne.viz.Brain.save_movie() function. "Factor by which to stretch time
            (default 4). For example, an epoch from -100 to 600 ms lasts 700 ms. With time_dilation=4 this
            would result in a 2.8 s long movie"..

        interpolation: str or None
            'interpolation' parameter in mne.viz.Brain.save_movie() function. "Interpolation method
            (scipy.interpolate.interp1d parameter). Must be one of ‘linear’, ‘nearest’, ‘zero’, ‘slinear’,
            ‘quadratic’, or ‘cubic’".

        time_viewer: bool
            'time_dilation' parameter in mne.viz.Brain.save_movie() function. "If True, include time viewer
            traces".
    Returns:
    """

    brain.save_movie(filename,
                     time_dilation=time_dilation,
                     tmin=brain.data['time'][0],
                     tmax=brain.data['time'][-1],
                     framerate=framerate,
                     interpolation=interpolation,
                     time_viewer=time_viewer)


def animate_matplot_brain(
    epoch=None,
    fwd='auto',
    stc='auto',
    views=[
        'lat',
        'dor',
        'fro'],
    size=200,
    hemi='both',
    colormap='mne',
    colorbar = True,
    colormap_limit_type='lims',
    cmin=None,
    cmid=None,
    cmax=None,
    spacing='oct5',
    smoothing_steps=3,
    timestamp=True,
    frame_rate=12,
    **kwargs
):
    """
    Creates an animated view of all timestamp observations an mne.epochs.Epochs data using a matplotlib backend.
    If multiple views are used then speed becomes significantly slower. Colorbar placement may be inconsistent.

    Parameters:
        epoch: mne.epochs.Epoch or None
            MNE epochs object containing portions of raw EEG data built around specified
            timestamp(s). If no fwd and stc are provided a fwd will be generated from the
            epoch using create_fsaverage_forward(). The epoch and fwd (either provided or
            generated) will then be used in create_inverse_solution() to generate an stc that
            the brain figure will be generated from.
        
        fwd: mne.forward.forward.Forward or 'auto'
            MNE forward object. If provided alongside an epoch they will both be used in
            create_fsaverage_forward() to create an stc which the brain figure will then be
            generated from. Defaults to 'auto'.

        stc: mne.source_estimate.SourceEstimate or 'auto'
            'inverse_solution' to generate the plot from. If set to "auto" then an stc will be
            automatically generated from either an epoch or an epoch and a fwd, however, this
            will significantly slow down rendering time. Defaults to 'auto'.

        views: str or list
            Specifies the 'view' parameter in the mne.SourceEstimate.plot() function. For any backend
            can be any combination of 'lat' (lateral), 'med' (medial), 'ros' (rostral), 'cau' (caudal),
            'dor' (dorsal), 'ven'(ventral), 'fro'(frontal), 'par' (parietal). The following arguments
            are also accepted but are NOT compatible with the matplotlib backend 'axi' (axial), 'sag'
            (sagittal), and 'cor'(coronal). Defaults to ['lat', 'fro', 'dor'].

        size: int
            Size will be divided by 100 and rounded the closest inch which will then be used as the
            height per view. For example, entering 100 will result in 1 inch per view. If plotting
            multiple views overall size of the multiplot is automatically calculated to fit all
            views. Defaults to 200.              

        hemi: 'lh’ or ‘rh’ or ‘both’ or ‘split’
            Specifies the 'initial_time' parameter in the mne.SourceEstimate.plot() function. Can be
            one of ‘lh’, ‘rh’, ‘both’, or ‘split’. Defaults to 'both'. Note that 'split' and 'both' will
            return a 'split' view since both is not avalible with a matplotlib backend. Defaults to 'both'.

        colormap: str or np.ndarray of float, shape(n_colors, 3 | 4)
            Specifies the 'colormap' parameter in the mne.SourceEstimate.plot() function. Can use a
            matplotlib colormap by name or take a custom look up table as input. Defaults to "mne".
    
        colorbar: bool
            Determines whether to include a colorbar on the plot not. Defaults to True.

        colormap_limit_type: str
            Can be either "lims" or "pos_lims". "lims" means that your cmin, cmid, and cmax values will specify the
            "Lower, middle, and upper bounds for colormap". Using "pos_lims" will lead to cmin, cmid, and cmax representing
            the "Lower, middle, and upper bound for colormap. Positive values will be mirrored directly across
            zero during colormap construction to obtain negative control points." Defaults to "lims".

        cmin: float
            Specifies the lower value of the colormap limit. If no value is specified then
            limits will be automatically calculated based on the mne.SourceEstimate.plot() function defaults OR
            will be the negative value of cmax if only that is provided.

        cmid: float
            Specifies the middle value of the colormap limit. If no value is specified then
            limits will be automatically calculated based on the mne.SourceEstimate.plot() function defaults OR
            will be the value between cmin and cmax if one/both of them is provided.

        cmax: float
            Specifies the middle value of the colormap limit. If no value is specified then
            limits will be automatically calculated based on the mne.SourceEstimate.plot() function defaults OR
            will be the negative value of cmin if only that is provided.

        spacing: str
            Specifies the 'spacing' parameter in the mne.SourceEstimate.plot() function. "The spacing to use for the
            source space. Can be 'ico#' for a recursively subdivided icosahedron, 'oct#' for a recursively subdivided
            octahedron. In general, you can speed up the plotting by selecting a sparser source
            space. Has no effect with mayavi backend. Defaults to ‘oct6’".

        smoothing_steps: int
            Specifies the 'smoothing_steps' parameter in the mne.SourceEstimate.plot() function. "The amount of smoothing".
            Defaults to 3.
            
        timestamp: bool
            Specifies whether or not to show the timestamp on the plot relative to the time in the epoch that
            is being shown. Defaults to True.

        frame_rate: int or float
            The frame rate to render the animation at. Defautls to 12.

    Returns:
        matplotlib.animation.FuncAnimation:
            Animation containing frames from all of the avalible times in the passed in epoch.
    """

    defaultKwargs = { 'transparent': False, 'alpha': 1.0, 'surface': 'inflated', 'cortex': 'classic',
                 'subject': None, 'time_label': None, 'time_unit': 's', 'volume_options': None,
                 'subjects_dir': None, 'title': None, 'show_traces': 'auto', 'src': None, 'verbose': None }
    kwargs = { **defaultKwargs, **kwargs }

    if isinstance(views, str):
        views = [views]

    if type(timestamp) is not bool:
        raise TypeError(
            """Passed timestamp object is not in the correct format, 
            please pass a bool (True/False) instead"""
        )
    
    if type(frame_rate) is not int and type(frame_rate) is not float:
        raise TypeError(
            """Passed frame_rate object is not in the correct format, 
            please pass an int object instead"""
        )
    
    if type(stc) is not mne.source_estimate.SourceEstimate and stc != 'auto':
        raise TypeError(
            """Passed stc object is not in the correct format, 
            please pass an mne.source_estimate.SourceEstimate object instead"""
        )

    if type(fwd) is not mne.forward.forward.Forward and fwd != 'auto':
        raise TypeError(
            """Passed fwd object is not in the correct format, 
            please pass an mne.forward.forward.Forward object or "auto" instead"""
        )
    
    # Calculate stc if it is not provided
    gen_stc = create_inverse_solution_auto(stc = stc, fwd = fwd, epoch = epoch)
    plot_stc = gen_stc.copy()

    frames_to_show = np.arange(0, plot_stc.data.shape[1], 1)

    ms_between_frames = 1000 / frame_rate

    def plotting(figure=None, recording_number=0, cbar = False, hemi = hemi, views = views):
        return (plot_topomap_3d_brain(stc=plot_stc,
                                      backend='matplotlib',
                                      hemi=hemi,
                                      views=views,
                                      colormap=colormap,
                                      colorbar = cbar,
                                      background='black',
                                      foreground = 'white',
                                      spacing=spacing,
                                      smoothing_steps=smoothing_steps,
                                      colormap_limit_type='lims',
                                      cmin=cmin,
                                      cmid=cmid,
                                      cmax=cmax,
                                      size=size,
                                      recording_number=recording_number,
                                      figure=figure,
                                      time_viewer = False,
                                      timestamp=False,
                                      **kwargs
                                      )
                )

    if (hemi == 'lh' and len(views) == 1) or (hemi == 'rh' and len(views) == 1):
        # Plotting for single view/hemi matplotlib.figure.Figure

        fig, ax = plt.subplots(round(size/100), round(size/100))
        
        def animate(frame_number):

            fig.clear()
            
            # get new image from list
            plotting(figure=fig,
                     recording_number=frame_number,
                     cbar = colorbar
                     )
            
            if timestamp:
                add_timestamp_brain(plot_stc, fig, frame_number, 0.18, 0.94, 15)

            return[fig]

    else:
        # Plotting for multi view/hemi matplotlib.image.AxesImage
        img_width = len(views)
        img_figsize = round(size / 100)
        
        if hemi == 'lh' or hemi == 'rh':
            img_height = 1
        else:
            img_height = 2
        
        fig, ax = plt.subplots(figsize = (img_figsize*img_width, img_figsize*img_height))
        
        add_colorbar = 0
        if colorbar:
            add_colorbar = 1
            colorbar = False
        
        # Generate dummy colorbar to move to the main figure
        if add_colorbar:
            cbar_width, cbar_height = calculate_cbar_dims(img_width, img_figsize, img_height)
            cbar_fig = plt.figure(figsize=(cbar_width, cbar_height))
            plotting(figure=cbar_fig, hemi='lh', views='fro', cbar=True)

        def animate(frame_number):
            # remove previous image
            ax.clear()
            plt.show(block=True)

            brain = plotting( 
                recording_number=frame_number,
                cbar = False
            )
            
            if add_colorbar:
                move_axes(cbar_fig.axes[1], brain, copy = True)
            
            if timestamp:
                if img_height == 2 and img_width == 1:
                    xpos = 0.1
                    ypos = 0.48
                else:
                    ypos = 0
                    xpos = 0.7
                    for i in range(img_width-2):
                        if img_width >= 3:
                            xpos += 0.1/(2**(i))
                
                add_timestamp_brain(plot_stc, brain, frame_number, xpos-0.01, ypos, 6*img_figsize)

            # Convert plot to image/frame
            plot_image = convert_figure_to_image(brain, img_height, img_width)

            # Remove gridlines 
            plt.setp(ax.get_xticklabels(), visible=False)
            plt.setp(ax.get_yticklabels(), visible=False)
            ax.tick_params(axis='both', which='both', length=0)
            # display new image
            ax.imshow(plot_image)
        
    ani = animation.FuncAnimation(
        fig,
        animate,
        frames=frames_to_show,
        interval=ms_between_frames,  # Time between frames in ms
        blit=False
    )

    return ani