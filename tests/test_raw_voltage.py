import pytest
#from simpl_eeg_capstone import raw_voltage

def test_raw_voltage_plot_0():
    """Test cases for plotting the raw voltage"""
    input_epoch = Epochs(experiment).data
    expected_output = "something" #read the output figure
    
    assert plot_voltage(input_epoch) == expected_ouput

    
def test_nonexistent_input_path():
    '''
    Testing input path
    '''
    with pytest.raises(FileNotFoundError):
        plot_volt("./srcc/999.fixica.set")