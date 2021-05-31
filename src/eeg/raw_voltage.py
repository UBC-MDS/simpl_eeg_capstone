def plot_voltage(epoch, **kwargs):
    """
    Return interactive raw voltage plot
    
    Parameters
    ----------
    epoch (mne.epochs.Epochs): Epoch to display #copy docs from mne
    **kwargs : arguments
               raw, events=None, duration=10.0, start=0.0, n_channels=20, bgcolor='w', color=None, bad_color=(0.8, 0.8, 0.8), event_color='cyan', 
               scalings=None, remove_dc=True, order=None, show_options=False, title=None, show=True, block=False, highpass=None, lowpass=None, 
               filtorder=4, clipping=1.5, show_first_samp=False, proj=True, group_by='type', butterfly=False, decim='auto', noise_cov=None, 
               event_id=None, show_scrollbars=True, show_scalebars=True, verbose=None)
    Returns
    ---------
    fig: matplotlib.figure.Figure
        The figure.
    """
    return epoch.plot(**kwargs)

# raw = mne.io.read_raw_eeglab(epoches)
# plot_voltage('C:/Users/mgaro/UBC-MDS/Capstone/simpl_eeg_capstone/data/fixica.set','C:/Users/mgaro/UBC-MDS/Capstone/simpl_eeg_capstone/data/fixica.svg' , duration =2)