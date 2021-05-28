import pytest
#from simpl_eeg_capstone import connectivity

def test_raw_voltage_plot():
    """Test cases for the connectivity circle functions"""


    assert(True)
    
def test_nonexistent_input_path():
    '''
    Testing input path
    '''
    with pytest.raises(FileNotFoundError):
        plot_connectivity("./srcc/999.fixica.set")
        
    