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
		Specifies the 'mindist' parameter in the mne.make_forward_solution() function

    n_jobs: int
		Specifies the 'n_jobs' parameter in the mne.make_forward_solution() function

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

    depth: depth
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
        display_time=None,
        views=[
            'lateral',
            'dorsal',
            'coronal',
            'frontal'],
        view_layout='horizontal',
        height_per_view=400,
        hemi='both',
        colormap='mne',
        colorbar_limit_type= 'pos_lims_value',
        colorbar_lims=[
                    0,
                    1.5,
                    3],
        colorbar=True,
        transparent=False,
        alpha=1.0,
        cortex='classic',
        background='black',
        foreground='white',
        spacing='oct6',
        smoothing_steps=0):
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
		Specifies the 'view' parameter in the mne.SourceEstimate.plot() function. Can be any of
		['lateral', 'medial', 'rostral', 'caudal', 'dorsal', 'ventral', 'frontal', 'parietal',
		'axial', 'sagittal', 'coronal']

	view_layout: str
		Specifies the 'view_layout' parameter in the mne.SourceEstimate.plot() function. Should be
		'vertical' or 'horizontal'. Using 'horizontal' with hemi set to 'split' might cause issues.

	height_per_view: int
		Specifies how many pixels tall each "view" of the brian will be. Height is automatically
		calculated based on the number of figures to ensure the dimensions always make all figures
		visible.

	hemi: str
		Specifies the 'initial_time' parameter in the mne.SourceEstimate.plot() function. Can be
		one of ‘lh’, ‘rh’, ‘both’, or ‘split’.

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

    # Calculate font size for colorbar/time label
    colorbar_font_size = round(height_per_view / 25)
    time_label_size = round(height_per_view / 33)

    # add 4/3 of the height in width for each visual
    if view_layout == "horizontal":
        auto_plot_size = [
            round(len(views) * (height_per_view * 4 / 3)), height_per_view]
    elif view_layout == "vertical":
        auto_plot_size = [
            round(
                height_per_view *
                4 /
                3),
            height_per_view *
            len(views)]

    if colorbar_limit_type == 'auto':
        clim_values = 'auto'
    else:
        if colorbar_limit_type == 'lims_value':
            clim_type = 'value'
            lims = 'lims'
        elif colorbar_limit_type == 'pos_lims_value':
            clim_type = 'value'
            lims = 'pos_lims'
        elif colorbar_limit_type == 'lims_percent':
            clim_type = 'percent'
            lims = 'lims'
        elif colorbar_limit_type == 'pos_lims_percent':
            clim_type = 'percent'
            lims = 'pos_lims'
        if lims == 'pos_lims':
            clim_values = dict(kind=clim_type, pos_lims=[colorbar_lims[0],
                                                         colorbar_lims[1],
                                                         colorbar_lims[2]]
                               )
        elif lims == 'lims':
            clim_values = dict(kind=clim_type, lims=[colorbar_lims[0],
                                                     colorbar_lims[1],
                                                     colorbar_lims[2]]
                               )

    brain = stc.plot(views=views,
                     surface='inflated',
                     # white is the other option (but I hate it)
                     hemi=hemi,
                     colormap=colormap,
                     size=auto_plot_size,
                     subject=None,
                     initial_time=display_time,
                     # For selecting image of individual frame.
                     clim=clim_values,
                     time_viewer=False,  # Use to open up interactive version
                     show_traces=False,
                     colorbar=colorbar,
                     transparent=transparent,  # Makes values below min fully transparent
                     alpha=alpha,  # used to make brain transparent
                     # figure = None, # used to attach to other figures
                     cortex=cortex,  # changes binarized curvature values
                     background=background,  # changes background color
                     foreground=foreground,  # changes color of display text
                     spacing=spacing,
                     # changes spacing for souce space. oct6 is default but can
                     # use lower number for speed
                     view_layout=view_layout,  # must be vertical when hemi is 'split'
                     smoothing_steps=smoothing_steps,
                     add_data_kwargs=dict(time_label_size=time_label_size,
                                          colorbar_kwargs=dict(label_font_size=colorbar_font_size)),

                     )

    return brain


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
