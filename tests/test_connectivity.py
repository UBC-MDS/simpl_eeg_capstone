import pytest
from simpl_eeg import eeg_objects, connectivity
import pandas as pd
import pickle
import matplotlib


# import the test data
with open('test_data/test_data.pkl', 'rb') as input:
    raw = pickle.load(input)

def test_calculate_connectivity():
    """Test cases for plotting the animated topographic map in a 3D head shape"""
    test_df = pd.DataFrame({"x":[1]})
    # check all inputs should be the correct format
    with pytest.raises(TypeError):
        connectivity.calculate_connectivity(test_df)
    with pytest.raises(TypeError):
        connectivity.calculate_connectivity(raw, calc_type=0)
    with pytest.raises(Exception):
        connectivity.calculate_connectivity(raw, calc_type="corr")
    
    # check all outpus are as expected
    output_df = connectivity.calculate_connectivity(raw)
    assert isinstance(output_df, pandas.core.frame.DataFrame)

def test_plot_connectivity():
    test_df = pd.DataFrame({"x":[1]})

    # check all inputs should be the correct format
    with pytest.raises(TypeError):
        connectivity.plot_connectivity(test_df)

    # check all outpus are as expected
    output_fig = connectivity.plot_connectivity(raw)
    assert isinstance(output_fig, matplotlib.figure.Figure)

    

def test_connectivity_circle():
    """
    Test on: plot_conn_circle
    data is a DataFrame
    Test cases for the connectivity circle functions
    """
    data = Epochs(experiment).data
    fig = matplotlib.figure #TODO: create empty figure
    calc_type = "max" #TODO: write the correct calc_type
    output_fig = plot_conn_circle(data,fig,calc_type)
    
    expected_fig = "something" #this should be a matplot.figure type, representing the expected output of the function
    
    assert expected_fig == output_fig
    
def test_nonexistent_input_path():
    '''
    Testing input path
    '''
    with pytest.raises(FileNotFoundError):
        plot_connectivity("./srcc/999.fixica.set")
        

def test_convert_pairs_2():
    '''
    Test on convert_pairs
    Tests input within range from PAIR OPTIONS
    '''
    
    in_string = "Fp1-F7, Fp2-F8"
    exp_out = [("Fp1", "F7"), ("Fp2","F8")]
    assert convert_pairs(in_string) == exp_out
    
def test_convert_pairs_3():
    '''
    Test on convert_pairs
    Tests input within range NOT from PAIR OPTIONS
    '''
    
    in_string = "mds-jk, mds-simpl"
    exp_out = [("mds", "jk"), ("mds","simpl")]
    assert convert_pairs(in_string) == exp_out
    # this test matches the function spec. Yet, within our context if the spec only accepted input from PAIR_OPTIONS then this test should check on a raised exception

print("All tests passed")