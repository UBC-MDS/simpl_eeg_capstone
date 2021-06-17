import mne
import matplotlib.pyplot as plt


def plot_voltage(epoch, remove_xlabel=False, **kwargs):
    """
    Generate raw voltage plot

    Args:
        epoch (mne.epochs.Epochs):
            Epoch(s) to display
        remove_xlabel (bool, optional):
            Whether to remove the x axis label. Defaults to False.
        **kwargs (dict, optional):
            Optional arguments to pass to mne.Epochs.plot()

            Full list of options available at
            https://mne.tools/stable/generated/mne.Epochs.html#mne.Epochs.plot

    Returns:
        matplotlib.figure.Figure:
            The raw voltage plot figure
    """
    if type(epoch) is not mne.epochs.Epochs:
        raise TypeError(
            "epoch is not an epoched data, "
            "please refer to eeg_objects to create an epoched data"
        )

    fig = epoch.plot(**kwargs)

    if remove_xlabel:
        fig.axes[0].get_xaxis().set_visible(False)

    return fig
