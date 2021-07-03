import pytest
from simpl_eeg import eeg_objects
import pickle
import mne


with open("tests/test_data/raw_1.pkl", "rb") as input:
    RAW_1 = pickle.load(input)

FOLDER = "experiment_folder"
PATH = "tests/test_data/"+FOLDER


def test_EEG_File():
    """Test EEF_File object creation"""

    with pytest.raises(FileNotFoundError):
        eeg_objects.EEG_File("invalid_path")

    # check attribute types
    eeg_file = eeg_objects.EEG_File(
        PATH,
        file_name="test.set"
    )
    assert eeg_file.experiment == FOLDER
    assert eeg_file.folder_path == PATH
    assert isinstance(eeg_file.raw, mne.io.eeglab.eeglab.RawEEGLAB)
    #assert isinstance(eeg_file.events, list)


def test_Epoch():
    epochs = eeg_objects.Epochs(
        PATH,
        file_name="test.set"
    )

    # check attribute types
    assert isinstance(epochs.eeg_file, eeg_objects.EEG_File)
    assert isinstance(epochs.all_epochs, mne.Epochs)
    assert isinstance(epochs.epoch, mne.Epochs)


if __name__ == '__main__':
    test_EEG_File()
    test_Epoch()
    print("All tests passed!")
