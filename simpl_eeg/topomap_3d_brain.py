import os
import os.path as op
import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mne.datasets import fetch_fsaverage
from mne.minimum_norm import make_inverse_operator


def create_fsaverage_forward(epochs, mindist=5.0, n_jobs=1):
    """
    A forward model is an estimation of the potential or field distribution for a known source
    and for a known model of the head. Returns EEG forward operator with a downloaded template
    MRI (fsaverage).

        Parameters
        ----------
        epochs : mne.epochs.Epochs
                MNE epochs object containing portions of raw EEG data built around specified timestamp(s)

        mindist: float
                Specifies the 'mindist' parameter in the mne.make_forward_solution() function. Defaults to 5.0

    n_jobs: int
                Specifies the 'n_jobs' parameter in the mne.make_forward_solution() function Defaults to 1

        Returns
        -------
        fwd: mne.forward.forward.Forward
        Forward operator built from the user_input epochs and the fsaverage brain.
    """

    # Download fsaverage files
    fs_dir = fetch_fsaverage(verbose=True)
    subjects_dir = op.dirname(fs_dir)

    # Used to download/load example MRI brain model
    # The files live in:
    subject = 'fsaverage'
    trans = 'fsaverage'  # MNE has a built-in fsaverage transformation
    src = op.join(fs_dir, 'bem', 'fsaverage-ico-5-src.fif')
    bem = op.join(fs_dir, 'bem', 'fsaverage-5120-5120-5120-bem-sol.fif')

    fwd = mne.make_forward_solution(epochs.info,
                                    trans=trans,
                                    src=src,
                                    bem=bem,
                                    eeg=True,
                                    mindist=mindist,
                                    n_jobs=n_jobs)

    return fwd


def create_inverse_solution(
        epochs,
        forward,
        epoch_num=0,
        covariance_method=[
            'empirical',
            'shrunk'],
        loose=0.2,
        depth=0.8,
        snr=3.0,
        inverse_epochs_method="dSPM",
        pick_ori='normal'):
    """
    Calculates the inverse solution, which is an Estimation of the unknown sources
    corresponding to the measured EEG or MEG.

        Parameters
        ----------
        epochs : mne.epochs.Epochs or mne.evoked.EvokedArray
                MNE epochs or evoked object containing portions of raw EEG data built around specified
                timestamp(s). The inverse solution will be built based on the data in the specified epoch.

    forward: mne.forward.forward.Forward
        Specifies the 'forward' parameter in the mne.minimum_norm.make_inverse_operator() function.

        epoch_num: int or str
                If input is an 'int' then this specifies which epoch in the 'epochs' number to build an
                inverse solution from. If input is "all" then an inverse solution will be built from all
                epochs.

        covariance_method: list
                Specifies the 'method' parameter in the mne.compute_covariance() function.

    loose: float
        Specifies the 'loose' parameter in the mne.minimum_norm.make_inverse_operator() function

    depth: float
        Specifies the 'depth' parameter in the mne.minimum_norm.make_inverse_operator() function

    snr: float
        Used to calculate 'lambda2' in the equation 'lambda2 = 1.0 / snr ** 2'

    inverse_epochs_method: str
        Specifies the 'method' parameter in mne.minimum_norm.apply_inverse_epochs() (if using epochs)
        or mne.minimum_norm.apply_inverse() (if using evoked data).

    pick_ori: str
        Specifies the 'pick_ori' parameter in mne.minimum_norm.apply_inverse_epochs() (if using epochs)
        or mne.minimum_norm.apply_inverse() (if using evoked data).

        Returns
        -------
        stc: mne.source_estimate.SourceEstimate
                Forward operator built from the user_input epochs and the fsaverage brain.
    """
    noise_cov = mne.compute_covariance(epochs, method=covariance_method)

    inverse_operator = make_inverse_operator(epochs.info, forward, noise_cov,
                                             loose=loose, depth=depth)

    lambda2 = 1.0 / snr ** 2

    if isinstance(epoch_num, int):
        epochs = epochs[epoch_num]

    # If epoch_num is any string other than "all" return false

    if isinstance(epochs, mne.epochs.Epochs):
        from mne.minimum_norm import apply_inverse_epochs
        stc = apply_inverse_epochs(epochs,
                                   inverse_operator=inverse_operator,
                                   lambda2=lambda2,
                                   method=inverse_epochs_method,
                                   pick_ori=pick_ori)
        stc = stc[0]

    elif isinstance(epochs, mne.evoked.EvokedArray):
        from mne.minimum_norm import apply_inverse
        stc = apply_inverse(epochs,
                            inverse_operator=inverse_operator,
                            lambda2=lambda2,
                            method=inverse_epochs_method,
                            pick_ori=pick_ori)

    return stc


def plot_topomap_3d_brain(
        epochs,
        stc='auto',
        display_time=0,
        backend='auto',
        views=[
            'lat',
            'fro',
            'dor'],
        view_layout='horizontal',
        size=300,
        hemi='both',
        colormap='mne',
        colorbar_limit_type='lims',
        cmin=None,
        cmid=None,
        cmax=None,
        colorbar=True,
        transparent=False,
        alpha=1.0,
        surface='inflated',
        cortex='classic',
        background='black',
        foreground='white',
        spacing='oct6',
        smoothing_steps=3,
        figure=None):
    """
    Creates a still image of the epochs or stc data mapped to the brain using the mne.SourceEstimate.plot
    function.

        Parameters
        ----------
        epochs : mne.epochs.Epochs or mne.evoked.EvokedArray
                MNE epochs or evoked object containing portions of raw EEG data built around specified
                timestamp(s) The inverse solution will be built based on the data in the specified epoch.

    stc: mne.source_estimate.SourceEstimate or str
                'inverse_solution' to generate the plot from. If set to "auto" then an stc will be
                automatically generated however, this will significantly increase running time.

        display_time: float or None
                Specifies the 'initial_time' parameter in the mne.SourceEstimate.plot() function to show
                a plot at a specific time.

        views: str or list
                Specifies the 'view' parameter in the mne.SourceEstimate.plot() function. FOR ANY BACKEND
        can be any combination of 'lat' (lateral), 'med' (medial), 'ros' (rostral), 'cau' (caudal),
        'dor' (dorsal), 'ven'(ventral), 'fro'(frontal), 'par' (parietal). The following arguments
        are also accepted but ARE NOT COPATIBLE WITH THE MATPLOTLIB BACKEND 'axi' (axial), 'sag'
        (sagittal), and 'cor'(coronal).

        view_layout: str
                Specifies the 'view_layout' parameter in the mne.SourceEstimate.plot() function. Should be
                'vertical' or 'horizontal'. Using 'horizontal' with hemi set to 'split' might cause issues.

        height: int
                Specifies how many pixels tall each "view" of the brian will be. Height is automatically
                calculated based on the number of figures to ensure the dimensions always make all figures
                visible. If using a matplotlib backend then the height will divided by 100 and rounded to
        the closest inch. For example, entering 100 will result in 1 inch per view.

        hemi: str
                Specifies the 'initial_time' parameter in the mne.SourceEstimate.plot() function. Can be
                one of ‘lh’, ‘rh’, ‘both’, or ‘split’. Defaults to 'both'.

        colormap: str or np.ndarray of float, shape(n_colors, 3 | 4)
                Specifies the 'colormap' parameter in the mne.SourceEstimate.plot() function. Can use a
                matplotlib colormap by name or take a custom look up table as input.

        colorbar_limit_type: str
                Can be one of "auto", "lims_value", "pos_lims_value", "lims_percent", or "pos_lims_percent".
                If set to "auto" then colorbar limits will be automatically calculated. If set to any of the
                other options a combination of "lims"/"pos_lims" and "value"/"percent" will be used to specify
                the colorbar type in the 'colorbar_lims' parameter.

        colorbar_lims: list, 3 elements
                Only used if colorbar_limit_type is set to anything other than "auto". Specifies the lower, middle,
                and upper bounds for colormap will be specified. If a "pos_lims" option was used then positive values
                will be mirrored directly across zero during colormap construction to obtain negative control points.

        colorbar: bool
                Specifies  the 'initial_time' parameter in the mne.SourceEstimate.plot() function. Determines
                whether to include a colorbar on the plot not.

        transparent: bool or None
                Specifies the 'transparent' parameter in the mne.SourceEstimate.plot() function

        alpha: str or list
                Specifies the 'alpha' parameter in the mne.SourceEstimate.plot() function

        cortex: str or tuple
                Specifies the 'cortex' parameter in the mne.SourceEstimate.plot() function

        background: matplotlib color
                Specifies the 'background' parameter in the mne.SourceEstimate.plot() function

        foreground: matplotlib color
                Specifies the 'foreground' parameter in the mne.SourceEstimate.plot() function

        spacing: str
                Specifies the 'spacing' parameter in the mne.SourceEstimate.plot() function

        smoothing_steps: int
                Specifies the 'smoothing_steps' parameter in the mne.SourceEstimate.plot() function

        Returns
        -------
        brain: mne.viz._brain._brain.Brain
        mne.viz figure of brain with input epoch or stc data mapped to it.
    """

    # if hemi == "split" and view_layout == 'horizontal':
    #     # Return warning that the horizontal with split isn't reccomended

    # Calculate stc if one is not provided
    if stc == 'auto':
        forward = create_fsaverage_forward(epochs)
        stc = create_inverse_solution(epochs, forward)

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
            auto_plot_size = [
                round(
                    size *
                    4 /
                    3),
                size *
                len(views)]

    else:
        colorbar_font_size = None
        time_label_size = None
        figsize = round(size / 100)
        if isinstance(views, str):
            views = [views]
        auto_plot_size = [size, size]

        import matplotlib.gridspec as gridspec

        def move_axes(ax, fig):
            # get a reference to the old figure context so we can release it
            old_fig = ax.figure

            # remove the Axes from it's original Figure context
            ax.remove()
            ax.figure = fig

            # add the Axes to the registry of axes for the figure
            fig.axes.append(ax)
            fig.add_axes(ax)

    # Set colorbar values
    if (cmin is None) and (cmax is None):
        clim_values = 'auto'
    else:
        if (cmin is None):
            cmin = -cmax
        if (cmax is None):
            cmax = -cmin
        if cmid is None:
            cmid = (cmin + cmax) / 2

        if colorbar_limit_type == 'lims':
            clim_values = dict(kind='value', lims=[
                cmin,
                cmid,
                cmax]
            )
        elif colorbar_limit_type == 'pos_lims':
            clim_values = dict(kind='value', pos_lims=[
                cmin,
                cmid,
                cmax]
            )

    def make_plot(
        epoch=epochs,
        stc=stc,
        views=views,
        hemi=hemi,
        colormap=colormap,
        surface=surface,
        size=auto_plot_size,
        subject=None,
        initial_time=display_time,
        clim=clim_values,
        time_viewer=False,  # Use to open up interactive version
        show_traces=False,
        colorbar=colorbar,
        transparent=transparent,
        alpha=alpha,
        figure=figure,
        cortex=cortex,
        background=background,
        foreground=foreground,
        spacing=spacing,
        backend=backend,
        view_layout=view_layout,
        smoothing_steps=smoothing_steps,
        time_label_size=time_label_size,
        label_font_size=colorbar_font_size,
    ):
        plt.show(block=True)

        brain = stc.plot(
            views=views,
            surface=surface,
            hemi=hemi,
            colormap=colormap,
            size=size,
            subject=None,
            initial_time=initial_time,
            clim=clim_values,
            time_viewer=False,
            show_traces=False,
            colorbar=colorbar,
            transparent=transparent,
            alpha=alpha,
            figure=figure,
            cortex=cortex,
            background=background,
            foreground=foreground,
            spacing=spacing,
            backend=backend,
            view_layout=view_layout,
            smoothing_steps=smoothing_steps,
            brain_kwargs=dict(
                show=False),
            add_data_kwargs=dict(
                time_label_size=time_label_size,
                colorbar_kwargs=dict(
                    label_font_size=colorbar_font_size)),
        )
        return brain

    if backend != 'matplotlib':
        return (make_plot())

    elif (hemi == 'lh' and len(views) == 1) or (hemi == 'rh' and len(views) == 1):
        return (make_plot(views=views[0]))

    else:

        from matplotlib.transforms import Bbox

        if hemi == 'both' or hemi == 'split':
            brain_hemi = ['lh', 'rh']

        else:
            brain_hemi = [hemi]

        img_width = len(views)
        img_height = len(brain_hemi)

        base_fig, ax = plt.subplots(
            figsize=(img_width * figsize, img_width * figsize), facecolor="black")
        plt.axis('off')

        add_colorbar = False

        # Set flag to generate colorbar later since adding it early causes bad
        # scaling
        if colorbar:
            colorbar = False
            add_colorbar = True

        x_pos = 0
        axes_pos = 1

        # Run to add new fig for each view
        for v in range(len(views)):

            y_pos = 0

            # run twice for each side of the brain if using both or split
            for h in range(len(brain_hemi)):

                plt.show(block=True)
                fig = plt.figure(figsize=(figsize, figsize))
                make_plot(
                    figure=fig,
                    hemi=brain_hemi[h],
                    views=str(
                        views[v]),
                    colorbar=colorbar)

                # Copy over the brain image only
                move_axes(fig.axes[0], base_fig)

                # Reposition copied over figure
                pos1 = base_fig.axes[1].get_position()
                pos2 = [
                    pos1.x0 + x_pos,
                    pos1.y0 + y_pos,
                    pos1.width,
                    pos1.height]
                base_fig.axes[axes_pos].set_position(pos2)  # 1, 3, 4, 5

                # Increment axes and positioning indexes
                axes_pos += 1
                y_pos = 1

            x_pos += 1

        # Generate dummy colorbar to move to the main figure
        if add_colorbar:
            #cbar_size = base_fig.get_size_inches()[0]/2

            cbar_width = img_width * figsize * 0.65

            if img_height == 2:
                cbar_height = img_height * figsize * 0.65
            else:
                cbar_height = img_height * 2 * figsize * 0.65

            if img_width >= 3:
                cbar_height = cbar_height * (img_width * 0.5)
                cbar_width = img_width * figsize * 0.85

            elif img_width >= 5:
                cbar_height = cbar_height * (img_width * 0.30)
                cbar_width = img_width * figsize * 0.4

            fig = plt.figure(figsize=(img_width * figsize * 0.65, cbar_height))
            make_plot(figure=fig, hemi='lh', views='fro', colorbar=True)
            move_axes(fig.axes[1], base_fig)

            pos2 = [pos1.x0 + 0, pos1.y0 + 1, pos1.width, pos1.height]

            print("axes_pos is " + str(axes_pos))
            base_fig.axes[axes_pos].set_position(pos2)

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

        Parameters
        ----------
    brain : brain: mne.viz._brain._brain.Brain
                mne.viz figure of brain which will be saved as a gif

    filename: str
                'filename' parameter in mne.viz.Brain.save_movie() function. "Path at which to save the movie.
                The extension determines the format (e.g., '*.mov', '*.gif', …; see the imageio documentation
                for available formats)".

        time_dilation: float
                'time_dilation' parameter in mne.viz.Brain.save_movie() function. "Factor by which to stretch time
                (default 4). For example, an epoch from -100 to 600 ms lasts 700 ms. With time_dilation=4 this
                would result in a 2.8 s long movie."

        interpolation: str or None
                'interpolation' parameter in mne.viz.Brain.save_movie() function. "Interpolation method
                (scipy.interpolate.interp1d parameter). Must be one of ‘linear’, ‘nearest’, ‘zero’, ‘slinear’,
                ‘quadratic’, or ‘cubic’."

    time_viewer: bool
                'time_dilation' parameter in mne.viz.Brain.save_movie() function. "If True, include time viewer
                traces".

        Returns
        -------
    """

    brain.save_movie(filename,
                     time_dilation=time_dilation,
                     tmin=brain.data['time'][0],
                     tmax=brain.data['time'][-1],
                     framerate=framerate,
                     interpolation=interpolation,
                     time_viewer=time_viewer)


def animate_matplot_brain(
    epochs,
    stc='auto',
    views=[
        'lat',
        'dor',
        'fro'],
    size=200,
    hemi='both',
    colormap='mne',
    colorbar_limit_type='lims',
    cmin=None,
    cmid=None,
    cmax=None,
    transparent=False,
    alpha=1.0,
    surface='inflated',
    cortex='classic',
    background='black',
    foreground='white',
    spacing='oct6',
    smoothing_steps=2,
    steps=3,
    frame_rate=12
):
    user_epoch=epochs
    import matplotlib.animation as animation

    if isinstance(views, str):
        views = [views]

    frames_to_show = round(user_epoch.times.shape[0] / steps)
    times_to_show = np.linspace(
        user_epoch.tmin,
        user_epoch.tmax,
        frames_to_show)

    # FOR TESTING ONLY DELETE LATER
    times_to_show = times_to_show[0:20]  # FOR TESTING ONLY DELETE LATER

    ms_between_frames = 1000 / frame_rate

    #fig = plt.figure(figsize = (3,3))

    fig, ax = plt.subplots()

    def plotting(figure=None, display_time=0):
        return (plot_topomap_3d_brain(epochs,
                                      stc=stc,
                                      backend='matplotlib',
                                      hemi=hemi,
                                      views=views,
                                      colormap=colormap,
                                      background=background,
                                      foreground=foreground,
                                      spacing=spacing,
                                      smoothing_steps=smoothing_steps,
                                      colorbar_limit_type='lims',
                                      cmin=cmin,
                                      cmid=cmid,
                                      cmax=cmax,
                                      size=size,
                                      display_time=display_time,
                                      figure=figure,
                                      transparent=transparent,
                                      alpha=alpha,
                                      surface=surface
                                      )
                )

    if (hemi == 'lh' and len(views) == 1) or (
            hemi == 'rh' and len(views) == 1):
        # Plotting for single view/hemi matplotlib.figure.Figure
        def animate(frame):

            fig.clear()
            # get new image from list
            plotting(figure=fig,
                     display_time=frame
                     )

            return[fig]

        ani = animation.FuncAnimation(
            brain,
            animate,
            frames=times_to_show,
            interval=ms_between_frames,  # Time between frames in ms
            blit=False
        )

    else:
        # Plotting for multi view/hemi matplotlib.image.AxesImage
        fig = plt.figure()
        ax = plt.gca()

        if views == 'lh' or views == 'rh':
            img_height = 1
        else:
            img_height = 2

        img_width = len(views)

        def animate(frame):
            # remove previous image
            ax.clear()

            plt.show(block=True)

            brain = plotting(  # figure = fig,
                display_time=frame
            )

            brain.canvas.draw()
            plot_image = np.frombuffer(
                brain.canvas.tostring_rgb(), dtype=np.uint8)
            plot_image = plot_image.reshape(
                brain.canvas.get_width_height()[::-1] + (3,))

            if (img_width > 2):
                cropped_height = round(
                    plot_image.shape[0] * (img_height / img_width) + plot_image.shape[0] * 0.07)
                cropped_height = plot_image.shape[1] - cropped_height
                plot_image = plot_image[cropped_height:, :, :]

            # display new image
            ax.imshow(plot_image)

        ani = animation.FuncAnimation(
            fig,
            animate,
            frames=times_to_show,
            interval=ms_between_frames,  # Time between frames in ms
            blit=False
        )

    return ani
