import mne


def plot_voltage(epoch, remove_xlabel=False, show_times=True, **kwargs):
    """
    Generate raw voltage plot

    Args:
        epoch (mne.epochs.Epochs):
            Epoch(s) to display
        remove_xlabel (bool, optional):
            Whether to remove the x axis label. Defaults to False.
        show_times (bool, optional):
            Whether to show seconds on the x axis. Defaults to True.
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
    ax = fig.axes[0]

    if remove_xlabel:
        ax.set_xlabel("")
        ax.minorticks_off()

    if show_times:
        event_time = epoch.events[0][2]

        ax.set_xticks([0, epoch.tmax-epoch.tmin])
        ax.set_xticklabels([
            "{:.2f} seconds".format(event_time+epoch.tmin),
            "{:.2f} seconds".format(event_time+epoch.tmax)
        ])

    return fig
