import pytest
#from simpl_eeg_capstone import raw_voltage

def test_connectivity_circle():
    """Test cases for plotting the raw voltage"""


    assert(True)

    
def test_nonexistent_input_path():
    '''
    Testing input path
    '''
    with pytest.raises(FileNotFoundError):
        plot_volt("./srcc/999.fixica.set")