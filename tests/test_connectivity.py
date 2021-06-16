import pytest
from simpl_eeg import connectivity
import pandas as pd
import numpy as np
import pickle
import matplotlib
import warnings
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')


# import the test data
with open('tests/test_data/test_data.pkl', 'rb') as input:
    EPOCH_1 = pickle.load(input)
with open('tests/test_data/test_data1.pkl', 'rb') as input:
    EPOCH_42 = pickle.load(input)


def test_calculate_connectivity():
    """Test cases for calculating connectivity"""

    # reject non-epoch data
    with pytest.raises(TypeError):
        test_df = pd.DataFrame({"x": [1]})
        connectivity.calculate_connectivity(test_df)

    # reject non-string calc_type 
    with pytest.raises(TypeError):
        connectivity.calculate_connectivity(EPOCH_1, calc_type=0)

    # reject invalid calc_type name
    with pytest.raises(Exception):
        connectivity.calculate_connectivity(EPOCH_1, calc_type="corr")

    # check that output type is a dataframe
    output_df = connectivity.calculate_connectivity(EPOCH_1)
    assert isinstance(output_df, pd.DataFrame)

    # check that calculation is NaN for a single frame
    expected_output = pd.DataFrame(
        index=EPOCH_1.ch_names,
        columns=EPOCH_1.ch_names,
        dtype=np.float64
    )
    pd.testing.assert_frame_equal(output_df, expected_output)


def test_plot_connectivity():
    """Test cases for plotting connectivity plot"""
    test_df = pd.DataFrame({"x": [1]})

    # check all inputs should be the correct format
    with pytest.raises(TypeError):
        connectivity.plot_connectivity(test_df)

    # check all outpus are as expected
    output_fig = connectivity.plot_connectivity(EPOCH_42)
    assert isinstance(output_fig, matplotlib.figure.Figure)
    plt.close("all")


def test_animate_connectivity():
    """Test cases for plotting animated connectivity plot"""
    test_df = pd.DataFrame({"x": [1]})

    # check all inputs should be the correct format
    with pytest.raises(TypeError):
        connectivity.animate_connectivity(test_df)

    # check all outpus are as expected
    output_ani = connectivity.animate_connectivity(EPOCH_42)
    assert isinstance(output_ani, matplotlib.animation.FuncAnimation)
    plt.close("all")


def test_connectivity_circle():
    """
    Test cases for the animated connectivity circle plot
    """
    test_df = pd.DataFrame({"x": [1]})

    # check all inputs should be the correct format
    with pytest.raises(TypeError):
        connectivity.animate_connectivity_circle(test_df)

    # check all outpus are as expected
    output_ani = connectivity.animate_connectivity_circle(EPOCH_42)
    assert isinstance(output_ani, matplotlib.animation.FuncAnimation)
    plt.close("all")


def test_plot_conn_circle():
    """Test cases for connectivity circle plot"""
    test_df = pd.DataFrame({"x": [1]})

    # check all inputs should be the correct format
    with pytest.raises(TypeError):
        connectivity.plot_conn_circle(test_df)

    # check output type is as expected
    output_fig = connectivity.plot_conn_circle(EPOCH_42)
    assert output_fig, matplotlib.figure.Figure
    plt.close("all")


def test_convert_pairs_1():
    '''
    Test convert_pairs helper function
    Tests input within range from PAIR OPTIONS
    '''

    in_string = "Fp1-F7, Fp2-F8"
    exp_out = [("Fp1", "F7"), ("Fp2", "F8")]
    assert connectivity.convert_pairs(in_string) == exp_out


def test_convert_pairs_2():
    '''
    Test on convert_pairs helper function
    Tests list format input
    '''

    in_string = [("Fp1", "F7"), ("Fp2", "F8")]
    exp_out = [("Fp1", "F7"), ("Fp2", "F8")]
    assert connectivity.convert_pairs(in_string) == exp_out


def test_convert_pairs_3():
    '''
    Test on convert_pairs helper function
    Tests empty list for indicating "all pairs"
    '''

    in_string = []
    exp_out = []
    assert connectivity.convert_pairs(in_string) == exp_out



if __name__ == '__main__':
    test_calculate_connectivity()
    test_plot_connectivity()
    test_animate_connectivity()
    test_connectivity_circle()
    test_plot_conn_circle()
    test_convert_pairs_1()
    test_convert_pairs_2()
    test_convert_pairs_3()
    print("All tests passed!")