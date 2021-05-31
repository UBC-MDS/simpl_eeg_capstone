import pytest
#from simpl_eeg_capstone import topomap_3d_brain


def test_create_fsaverage_forward():
    """Test cases for plotting 3D image mapped to the brain """
    input_epoch = Epochs(experiment).data
    expected_output = "something" #read the output data: of type mne.forward
    
    assert  create_fsaverage_forward(input_epoch) == expected_ouput
    
def test_plot_topomap_3d_brain():
    """Test cases for plotting 3D image mapped to the brain """
    input_epoch = Epochs(experiment).data
    expected_output = "something" #read the output figure
    
    assert  plot_topomap_3d_brain(input_epoch) == expected_ouput


def test_nonexistent_input_path():
    '''
    Testing input path
    '''
    with pytest.raises(FileNotFoundError):
        plot_topomap_3d_brain("./srcc/999.fixica.set")