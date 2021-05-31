import numpy as np
import mne
import scipy.io

class eeg_file:

    def __init__(self, experiment):
        self.experiment = experiment
        self.mat = scipy.io.loadmat("data/"+experiment+"/impact locations.mat")
        self.raw = mne.io.read_raw_eeglab("data/"+experiment+"/fixica.set")


class epochs:

    def __init__(self, experiment, duration=2, start_second=None):
        self.eeg_file = eeg_file(experiment)
        self.data = self.generate_epochs(duration, start_second)

    def generate_epochs(self, duration, start_second):
        if start_second:
            start_time = start_second*2049
            stim_mock = [[start_time]]
            tmin = 0
            tmax = duration
        else:
            stim_mock = self.eeg_file.mat["elecmax1"]
            tmin = -0.3
            tmax = tmin + duration
            print(tmax)

        events = [[i, 0, 1] for i in stim_mock[0]]
        event_dict = {"header": 1}

        epochs = mne.Epochs(
            self.eeg_file.raw,
            events,
            tmin=tmin,
            tmax=tmax,
            event_id=event_dict,
            preload=True,
            baseline=(0, 0)
        )
        return epochs

    def generate_evoked(self):
        evoked = self.data["header"].average()
        return evoked
    
    def get_nth_epoch(self, n):
        """Return the nth epoch from the raw data

        Args:
            n (int): The number of the epoch
        """
        return self.data[n]