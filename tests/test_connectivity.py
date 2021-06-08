import pytest
from simpl_eeg import eeg_objects, connectivity
import pandas as pd
import pickle
import matplotlib
import warnings
warnings.filterwarnings('ignore')


# import the test data
with open('data/test_data/test_data.pkl', 'rb') as input:
    raw = pickle.load(input)
with open('data/test_data/test_data1.pkl', 'rb') as input:
    raw1 = pickle.load(input)


def test_calculate_connectivity():
    """Test cases for calculating connectivity"""
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
    assert isinstance(output_df, pd.DataFrame)

def test_plot_connectivity():
    """Test cases for plotting connectivity plot"""
    test_df = pd.DataFrame({"x":[1]})

    # check all inputs should be the correct format
    with pytest.raises(TypeError):
        connectivity.plot_connectivity(test_df)

    # check all outpus are as expected
    output_fig = connectivity.plot_connectivity(raw)
    assert isinstance(output_fig, matplotlib.figure.Figure)

def test_animate_connectivity():
    """Test cases for plotting animated connectivity plot"""
    test_df = pd.DataFrame({"x":[1]})

    # check all inputs should be the correct format
    with pytest.raises(TypeError):
        connectivity.animate_connectivity(test_df)

    # check all outpus are as expected
    output_ani = connectivity.animate_connectivity(raw1)
    assert isinstance(output_ani, matplotlib.animation.FuncAnimation)
    

def test_connectivity_circle():
    """
    Test cases for the animated connectivity circle plot
    """
    test_df = pd.DataFrame({"x":[1]})

    # check all inputs should be the correct format
    with pytest.raises(TypeError):
        connectivity.animate_connectivity_circle(test_df)

    # check all outpus are as expected
    output_ani = connectivity.animate_connectivity_circle(raw1)
    assert isinstance(output_ani, matplotlib.animation.FuncAnimation)
    
def test_plot_conn_circle():
    """Test cases for connectivity circle plot"""
    test_df = pd.DataFrame({"x":[1]})

    # check all inputs should be the correct format
    with pytest.raises(TypeError):
        connectivity.plot_conn_circle(test_df)
    
    # check all outpus are as expected
    output_fig = connectivity.plot_conn_circle(raw1)
    assert isinstance(output_fig, matplotlib.figure.Figure)


        

def test_convert_pairs_2():
    '''
    Test on convert_pairs
    Tests input within range from PAIR OPTIONS
    '''
    
    in_string = "Fp1-F7, Fp2-F8"
    exp_out = [("Fp1", "F7"), ("Fp2","F8")]
    assert connectivity.convert_pairs(in_string) == exp_out
    
def test_convert_pairs_3():
    '''
    Test on convert_pairs
    Tests input within range NOT from PAIR OPTIONS
    '''
    
    in_string = "mds-jk, mds-simpl"
    exp_out = [("mds", "jk"), ("mds","simpl")]
    assert connectivity.convert_pairs(in_string) == exp_out
    # this test matches the function spec. Yet, within our context if the spec only accepted input from PAIR_OPTIONS then this test should check on a raised exception

if __name__ == '__main__':
    test_calculate_connectivity()
    test_plot_connectivity()
    test_animate_connectivity()
    test_connectivity_circle()
    test_plot_conn_circle()
    test_convert_pairs_2()
    test_convert_pairs_3()
    print("All tests passed!")