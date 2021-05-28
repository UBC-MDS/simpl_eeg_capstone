import pytest
#from simpl_eeg_capstone import topomap_3d_brain


def test_plot_topomap_3d_brain():
    """Test cases for plotting 3D image mapped to the brain """


    assert(True)


def test_nonexistent_input_path():
    '''
    Testing input path
    '''
    with pytest.raises(FileNotFoundError):
        plot_topomap_3d_brain("./srcc/999.fixica.set")