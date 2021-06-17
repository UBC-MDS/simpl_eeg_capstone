import pickle
import mne
import numpy
import pandas as pd
import plotly
import pytest
from simpl_eeg import eeg_objects, topomap_3d_head

# import the test data
with open("tests/test_data/test_data.pkl", "rb") as input:
    raw = pickle.load(input)
with open("tests/test_data/test_data1.pkl", "rb") as input:
    epoch42 = pickle.load(input)

# test the animate_3d_head function
def test_animate_3d_head():
    """Test cases for plotting the animated topographic map in a 3D head shape"""
    test_df = pd.DataFrame({"x": [1]})

    # reject non-epoch data
    with pytest.raises(TypeError):
        topomap_3d_head.animate_3d_head(test_df)

    # reject non-string plot_title
    with pytest.raises(TypeError):
        topomap_3d_head.animate_3d_head(raw, plot_title=0)

    # reject non-string color_title
    with pytest.raises(TypeError):
        topomap_3d_head.animate_3d_head(raw, color_title=0)

    # reject non-string color_map
    with pytest.raises(TypeError):
        topomap_3d_head.animate_3d_head(raw, colormap=0)

    # reject non-numeric inputs for color_min and color_max
    with pytest.raises(TypeError):
        topomap_3d_head.animate_3d_head(raw, color_min="0")
    with pytest.raises(TypeError):
        topomap_3d_head.animate_3d_head(raw, color_max="0")

    # check all outputs are as expected
    ani = topomap_3d_head.animate_3d_head(epoch42)
    ani2 = topomap_3d_head.animate_3d_head(epoch42, color_min=-30, color_max=40)
    assert isinstance(ani, plotly.graph_objs._figure.Figure)
    assert ani2.data[0]["cmin"] == -30 and ani2.data[0]["cmax"] == 40


# test the topo_3d_map function
def test_topo_3d_map():
    """Test cases for plotting the static topographic map in a 3D head shape"""
    test_df = pd.DataFrame({"x": [1]})

    # reject non-epoch data
    with pytest.raises(TypeError):
        topomap_3d_head.topo_3d_map(test_df)

    # reject non-string plot_title
    with pytest.raises(TypeError):
        topomap_3d_head.topo_3d_map(raw, plot_title=0)

    # reject non-string color_title
    with pytest.raises(TypeError):
        topomap_3d_head.topo_3d_map(raw, color_title=0)

    # reject non-string color_map
    with pytest.raises(TypeError):
        topomap_3d_head.topo_3d_map(raw, colormap=0)

    # reject non-numeric inputs for color_min and color_max
    with pytest.raises(TypeError):
        topomap_3d_head.topo_3d_map(raw, color_min="0")
    with pytest.raises(TypeError):
        topomap_3d_head.topo_3d_map(raw, color_max="0")

    # check all outputs are as expected
    ani = topomap_3d_head.topo_3d_map(epoch42, time_stamp=0)
    ani2 = topomap_3d_head.topo_3d_map(
        epoch42, time_stamp=0, color_min=-30.2, color_max=40
    )
    assert isinstance(ani, plotly.graph_objs._figure.Figure)
    assert ani2.data[0]["cmin"] == -30.2 and ani2.data[0]["cmax"] == 40


def test_frame_args():
    """Test cases for returning the correct arguments for animation"""
    with pytest.raises(TypeError):
        topomap_3d_head.frame_args(duration="0")

    # check all outputs are as expected
    return_dict = topomap_3d_head.frame_args(duration=12)
    assert return_dict["frame"]["duration"] == 12
    assert return_dict["mode"] == "immediate"
    assert return_dict["fromcurrent"] is True
    assert return_dict["transition"]["duration"] == 12
    assert return_dict["transition"]["redraw"] is False


def test_get_standard_coord():
    """Test cases for getting standard electrode node information"""
    montage, standard_coord_array = topomap_3d_head.get_standard_coord()
    assert type(montage) == mne.channels.montage.DigMontage
    assert type(standard_coord_array) == numpy.ndarray
    # there should be xyz coordinate for 343 electrode nodes
    assert standard_coord_array.shape == (343, 3)


def test_get_eeg_node():
    """Test cases for getting electrode location from the raw data"""
    test_df = pd.DataFrame({"x": [1]})
    standard_montage, standard_coord = topomap_3d_head.get_standard_coord()

    # reject non-df data
    with pytest.raises(TypeError):
        topomap_3d_head.get_eeg_node(test_df, standard_montage)

    # reject non-mne.montage input
    with pytest.raises(TypeError):
        topomap_3d_head.get_eeg_node(epoch42, standard_coord)

    standard_montage, standard_coord = topomap_3d_head.get_standard_coord()
    node_array = topomap_3d_head.get_eeg_node(epoch42, standard_montage)
    # there should be xyz coordinate for 19 electrode nodes
    assert node_array.shape == (19, 3)
    assert type(node_array) == numpy.ndarray


def test_get_node_dataframe():
    """Test cases for saving electrode node location into a dataframe"""
    test_df = pd.DataFrame({"x": [1]})
    standard_montage, standard_coord = topomap_3d_head.get_standard_coord()

    # reject non-df data
    with pytest.raises(TypeError):
        topomap_3d_head.get_node_dataframe(test_df, standard_montage)

    # reject non-mne.montage input
    with pytest.raises(TypeError):
        topomap_3d_head.get_node_dataframe(epoch42, standard_coord)

    node_df = topomap_3d_head.get_node_dataframe(epoch42, standard_montage)
    # check all outputs should be as expected
    assert type(node_df) == pd.core.frame.DataFrame
    assert node_df.shape == (19, 4)
    assert node_df.columns.values[0] == "channel"
    assert node_df.columns.values[1] == "X"
    assert node_df.columns.values[2] == "Y"
    assert node_df.columns.values[3] == "Z"


def test_interpolated_time():
    """Test cases for running the 3D interpolation"""
    channel_names = epoch42.ch_names
    standard_montage, standard_coord = topomap_3d_head.get_standard_coord()
    node_coord = topomap_3d_head.get_eeg_node(epoch42, standard_montage)
    x = numpy.array(standard_coord)[:, 0]
    y = numpy.array(standard_coord)[:, 1]
    z = numpy.array(standard_coord)[:, 2]

    # reject non-df data
    with pytest.raises(TypeError):
        topomap_3d_head.interpolated_time(
            epoch42, channel_names, node_coord, x, y, z, 1
        )

    # reject non-list channel_names
    with pytest.raises(TypeError):
        topomap_3d_head.interpolated_time(
            epoch42.to_data_frame(), "channel_names", node_coord, x, y, z, 1
        )

    # reject non-array node_coord
    with pytest.raises(TypeError):
        topomap_3d_head.interpolated_time(
            epoch42.to_data_frame(), "channel_names", channel_names, x, y, z, 1
        )

    # reject non-array x, y, z
    with pytest.raises(TypeError):
        topomap_3d_head.interpolated_time(
            epoch42.to_data_frame(), channel_names, node_coord, 1, y, z, 1
        )
    with pytest.raises(TypeError):
        topomap_3d_head.interpolated_time(
            epoch42.to_data_frame(), channel_names, node_coord, x, 1, z, 1
        )
    with pytest.raises(TypeError):
        topomap_3d_head.interpolated_time(
            epoch42.to_data_frame(), channel_names, node_coord, x, y, 1, 1
        )

    output = topomap_3d_head.interpolated_time(
        epoch42.to_data_frame(), channel_names, node_coord, x, y, z, 1
    )
    # check all outputs should be as expected
    assert output.shape == (343,)
    assert type(output) == numpy.ndarray


if __name__ == "__main__":
    test_animate_3d_head()
    test_topo_3d_map()
    test_frame_args()
    test_get_standard_coord()
    test_get_eeg_node()
    test_get_node_dataframe()
    test_interpolated_time()
    print("All tests passed!")