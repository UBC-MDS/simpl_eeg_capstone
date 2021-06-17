import mne
import matplotlib.pyplot as plt
def plot_voltage(epoch, remove_xlabel=False, **kwargs):
    """
    Return interactive raw voltage plot
    
    Parameters
    ----------
    epoch (mne.epochs.Epochs): Epoch to display
    remove_xlabel (bool, optional): Whether to remove the x axis label. Defaults to False.
    **kwargs : arguments
               raw, events=None, duration=10.0, start=0.0, n_channels=20, bgcolor='w', color=None, bad_color=(0.8, 0.8, 0.8), event_color='cyan', 
               scalings=None, remove_dc=True, order=None, show_options=False, title=None, show=True, block=False, highpass=None, lowpass=None, 
               filtorder=4, clipping=1.5, show_first_samp=False, proj=True, group_by='type', butterfly=False, decim='auto', noise_cov=None, 
               event_id=None, show_scrollbars=True, show_scalebars=True, verbose=None)
    """
    if type(epoch) is not mne.epochs.Epochs:
        raise TypeError("epoch is not an epoched data, please refer to eeg_objects to create an epoched data")
    fig = epoch.plot(**kwargs)

    if remove_xlabel:
        fig.axes[0].get_xaxis().set_visible(False)

    return fig
