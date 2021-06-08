import mne
import scipy.io


class EEG_File:
    """
    A class to import and store relevant eeg files

    Attributes
    ----------
    experiment : str
        experiment folder name within the data folder
    mat : list(int)
        a list of integers representing impact times
    raw : mne.io.Raw
        raw experiment data in FIF format
    """

    def __init__(self, experiment):
        self.experiment = experiment
        self.mat = scipy.io.loadmat("data/"+experiment+"/impact locations.mat")
        self.raw = mne.io.read_raw_eeglab("data/"+experiment+"/fixica.set")


class Epochs:
    """
    A class to represent epochs and underlying data

    Attributes
    ----------
    eeg_file : EEG_File
        eeg file data
    data : mne.Epochs
        the generated epoch data
    epoch : mne.Epochs
        the selected epoch

    Methods
    -------
    generate_epochs(duration, start_second):
        Calculates epochs based on a duration and start second
    get_nth_epoch(duration, n):
        Returns the nth epoch
    get_fram(tmin, step_size, frame_number):
        Calculates a subset of the epoch based on the step size and frame
    """

    def __init__(self, experiment, tmin=-0.3, tmax=0.7, start_second=None):
        self.eeg_file = EEG_File(experiment)
        self.data = self.generate_epochs(tmin, tmax, start_second)
        self.epoch = self.set_nth_epoch(0)

    def generate_epochs(self, tmin, tmax, start_second):
        freq = int(self.eeg_file.raw.info["sfreq"])
        if start_second:
            start_time = start_second*freq
            stim_mock = [[start_time]]
        else:
            stim_mock = self.eeg_file.mat["elecmax1"]

        events = [[ts, 0, ts//freq] for i, ts in enumerate(stim_mock[0])]
        epochs = mne.Epochs(
            self.eeg_file.raw,
            events,
            event_id={str(i[2])+" seconds": i[2] for i in events},
            tmin=tmin,
            tmax=tmax,
            preload=True,
            baseline=(0, 0)
        )

        return epochs

    def set_nth_epoch(self, n):
        """
        Set the nth epoch from the raw data

        Args:
        n (int): The epoch to select
        """

        self.epoch = self.data[n]

    def get_nth_epoch(self):
        """
        Return the nth epoch from the raw data

        Returns:
            mne: The epoch of interest
        """
        return self.epoch

    def skip_n_steps(self, num_steps):
        """
        Return new epoch containing every nth frame

        Args:
        n (int): The number of time steps to skip

        Returns:
            mne.Epochs: The reduced epoch
        """

        return self.epoch.copy().decimate(num_steps)

