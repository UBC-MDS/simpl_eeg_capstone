import pytest
#from simpl_eeg_capstone import topomap_2d


def test_animate_topomap_2d():
    """Test cases for the animation plot function"""


    assert(True)

    
def test_nonexistent_input_path():
    '''
    Testing input path
    '''
    with pytest.raises(FileNotFoundError):
        plot_topomap_2d("./srcc/999.fixica.set")    