import pytest
from simpl_eeg import raw_voltage, eeg_objects
import pandas as pd
import pickle
import mne

# import the test data
with open('test_data/test_data1.pkl', 'rb') as input:
    raw1 = pickle.load(input)

def test_raw_voltage_plot():
    """Test cases for plotting the raw voltage"""
    test_df = pd.DataFrame({"x":[1]})

    # check all inputs should be the correct format
    with pytest.raises(TypeError):
        raw_voltage.plot_voltage(test_df)
    
    # check all outpus are as expected
    output_fig = raw_voltage.plot_voltage(raw1)
    assert isinstance(output_fig, mne.viz._figure.MNEBrowseFigure)


if __name__ == '__main__':
    test_raw_voltage_plot()
    print("All tests passed!")   