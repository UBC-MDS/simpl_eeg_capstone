import os
import os.path as op
import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mne.datasets import fetch_fsaverage
from mne.minimum_norm import make_inverse_operator


def create_fsaverage_forward(epoch, mindist = 5.0, n_jobs = 1):
	# Make EEG forward operator with a downlaoded template MRI (fsaverage).
	# Forward model is an estimation of the potential or field distribution for a known source
	# and for a known model of the head
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
	                                mindist = mindist,
	                                n_jobs = n_jobs)

		return fwd


# Currently a bunch of functions are needed to create the one object we need to
# make a 3D brain map. It might be better to make super one pipeline function to
# get straight to the desired object.

def compute_covariance(epoch, method = ['empirical', 'shrunk']):
# Used to create averaged out MRI data
	return (mne.compute_covariance(epoch, method = method))

def load_covariance(patient_number):
	# not implemented yet
	n = patient_number

def create_inverse_operator(epoch, forward, noise_cov, loose = 0.2, depth = 0.8):
	# creates inverse operator which then gets used in the inverse solution
	return (make_inverse_operator(epoch.info, forward, noise_cov, loose= loose, depth=depth))

def create_inverse_solution(epoch, inverse_operator, epoch_num = 0, snr = 3.0,
	method = "dSPM", pick_ori = 'normal'):
# Estimation of the unknown sources corresponding to the measured EEG or MEG
# is referred to as inverse modeling
	# currently using defaults from MNE documentation for values 
	lambda2 = 1.0 / snr ** 2

	if type(epoch) == mne.epochs.Epochs:
		from mne.minimum_norm import apply_inverse_epochs
		stc = apply_inverse_epochs(epoch[epoch_num],
                    inverse_operator = inverse_operator,
            		lambda2 = lambda2,
                    method = method,
                    pick_ori = pick_ori)
		stc = stc[0]

	elif type(epoch) == mne.evoked.EvokedArray:
		from mne.minimum_norm import apply_inverse
		stc = apply_inverse_epochs(epoch,
            inverse_operator = inverse_operator,
            lambda2 = lambda2,
            method = method,
            pick_ori = pick_ori)

	return stc


def plot_topomap_3d_brain(stc, timestamp = 0, views = ['lateral', 'dorsal','coronal', 'frontal'],
	view_layout = 'horizontal', pixel_height_per_view = 400, hemi = 'both', colormap = 'mne',
	colorbar_limit_type = 'auto', colorbar_lims = [0, 8, 10], colorbar = True,
	transparent = False, alpha = 1.0, cortex = 'classic', background = 'black', spacing = 'oct6',
	smoothing_steps = 10):
	# if hemi == "split" and view_layout == 'horizontal':
	#     # Return warning that the horizontal with split isn't reccomended

	# Calculate font size for colorbar/time label
	colorbar_font_size = round(pixel_height_per_view/25)
	time_label_size = round(pixel_height_per_view/33)


	# add 4/3 of the height in width for each visual
	if view_layout == "horizontal":
	    auto_plot_size = [round(len(views) * (pixel_height_per_view * 4/3)), pixel_height_per_view] 
	elif view_layout == "vertical":
	    auto_plot_size = [round(pixel_height_per_view * 4/3), pixel_height_per_view * len(views)] 

	if colorbar_limit_type == 'auto':
	    clim_values = 'auto'
	else:
	    if colorbar_limit_type == 'lims_value':
	        clim_type = 'value'; lims = 'lims'
	    elif colorbar_limit_type == 'pos_lims_value':
	        clim_type = 'value'; lims = 'pos_lims'
	    elif colorbar_limit_type == 'lims_percent':
	        clim_type = 'percent'; lims = 'lims'
	    elif colorbar_limit_type == 'pos_lims_percent':
	        clim_type = 'percent'; lims = 'pos_lims'
	    if lims == 'pos_lims':
	        clim_values = dict(kind=clim_type,pos_lims=[colorbar_lims[0],
	                                                    colorbar_lims[1],
	                                                    colorbar_lims[2]]
	                          )
	    elif lims == 'lims':
	        clim_values = dict(kind=clim_type,lims=[colorbar_lims[0],
	                                                colorbar_lims[1],
	                                                colorbar_lims[2]]
	                          )

	brain = stc.plot(views= views,
	                 surface = 'inflated', # white is the other option (but I hate it)
	                 hemi = hemi,
	                 colormap = colormap,
	                 size = auto_plot_size,
	                 subject= None,
	                 initial_time = timestamp, # For selecting image of individual frame.
	                 clim = clim_values,
	                 time_viewer = False, # Use to open up interactive version
	                 show_traces = False,
	                 colorbar = colorbar, 
	                 transparent = transparent, # Makes values below min fully transparent
	                 alpha = alpha, # used to make brain transparent
	                 #figure = None, # used to attach to other figures
	                 cortex = cortex, # changes binarized curvature values
	                 background = background, # changes background color
	                 #foreground = "white", # changes color of display text
	                 spacing = spacing, #changes spacing for souce space. oct6 is default but can use lower number for speed
	                 view_layout = view_layout, # must be vertical when hemi is 'split'
	                 smoothing_steps = smoothing_steps,
	                 add_data_kwargs = dict(time_label_size=time_label_size, 
	                                        colorbar_kwargs = dict(label_font_size = colorbar_font_size)), 
	               
	                );

	return brain


def animate_topomap_3d_brain(stc, file_name, views = ['lateral', 'dorsal','coronal', 'frontal'],
	framerate = 12, interpolation = 'linear', time_dilation = 20, view_layout = 'horizontal',
	pixel_height_per_view = 200, hemi = 'both', colormap = 'mne', colorbar_limit_type = 'auto',
	colorbar_lims = [0, 8, 10], colorbar = True, transparent = False, alpha = 1.0, cortex = 'classic',
	background = 'black', spacing = 'oct6', smoothing_steps = 10):

	brain = plot_topomap_3d_brain(stc, timestamp = 0, views = views,
	view_layout = view_layout, pixel_height_per_view = pixel_height_per_view, hemi = hemi, colormap = colormap,
	colorbar_limit_type = colorbar_limit_type, colorbar_lims = colorbar_lims, colorbar = colorbar,
	transparent = transparent, alpha = alpha, cortex = cortex, background = background, spacing = spacing,
	smoothing_steps = smoothing_steps)

	brain.save_movie(file_name,
                 time_dilation = time_dilation,
                 tmin = stc.tmin,
                 tmax = stc.times[-1],
                 framerate = framerate,
                 interpolation=interpolation,
                 time_viewer=True)



