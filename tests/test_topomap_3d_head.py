import pytest
#from simpl_eeg_capstone import topomap_3d_head


def test_animate_3d_head():
    """Test cases for plotting the topographic map in a 3D head shape"""


    assert(True)

    
def test_nonexistent_input_path():
    '''
    Testing input path
    '''
    with pytest.raises(FileNotFoundError):
        animate_3d_head("./srcc/999.fixica.set")