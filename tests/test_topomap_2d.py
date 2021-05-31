import pytest
#from simpl_eeg_capstone import topomap_2d


def test_plot_topomap_2d_0():
    """Test cases for the animation plot function: within input space"""
    input_epoch = Epochs(experiment).data
    expected_output = "something" #read the output figure
    
    assert plot_topomap_2d(input_epoch) == expected_ouput #TIP: this comparison might not work. reason is the datatype is not compatible with "==". find the comparison specific to this datatype

def test_plot_topomap_2d_1():
    """Test cases for the animation plot function: wrong datatype for colorbar"""
    input_epoch = Epochs(experiment).data
    with pytest.raises(AttributeError):
        plot_topomap_2d(input_epoch, colorbar = "mds")

def test_nonexistent_input_path():
    '''
    Testing input path
    '''
    with pytest.raises(FileNotFoundError):
        plot_topomap_2d("./srcc/999.fixica.set")
        
def test_animate_topomap_2d_0():
    """Test cases for the animation plot function: within input space"""
    input_epoch = Epochs(experiment).data
    expected_output = "something" #read the output animation
    
    assert animate_topomap_2d(input_epoch) == expected_ouput #TIP: this comparison might not work. reason is the datatype is not compatible with "==". find the comparison specific to this datatype