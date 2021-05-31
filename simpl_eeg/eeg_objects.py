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

    def __init__(self, experiment, duration=2, start_second=None):
        self.eeg_file = EEG_File(experiment)
        self.data = self.generate_epochs(duration, start_second)
        self.epoch = self.get_epoch(0)

    def generate_epochs(self, duration, start_second):
        freq = int(self.eeg_file.raw.info["sfreq"])
        if start_second:
            start_time = start_second*freq
            stim_mock = [[start_time]]
            tmin = 0
            tmax = duration
        else:
            stim_mock = self.eeg_file.mat["elecmax1"]
            tmin = -0.3
            tmax = tmin + duration

        events = [[ts, 0, ts//freq] for i, ts in enumerate(stim_mock[0])]
        epochs = mne.Epochs(
            self.eeg_file.raw,
            events,
            tmin=tmin,
            tmax=tmax,
            preload=True,
            baseline=(0, 0)
        )

        return epochs

    def get_nth_epoch(self, n):
        """
        Return the nth epoch from the raw data

        Args:
        n (int): The epoch to select
        """

        return self.data[n]

    def get_frame(self, tmin, step_size, frame_number):
        return self.epoch.copy().crop(
            tmin=tmin+step_size*frame_number,
            tmax=tmin+step_size*(frame_number+1),
            include_tmax=False
        )
