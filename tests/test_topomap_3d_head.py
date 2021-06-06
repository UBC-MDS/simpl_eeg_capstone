from simpl_eeg import eeg_objects, topomap_3d_head
import pandas as pd
import pickle
import plotly

# import the test data
with open('test_data/test_data.pkl', 'rb') as input:
    raw = pickle.load(input)

# test the animate_3d_head function
def test_animate_3d_head():
    """Test cases for plotting the animated topographic map in a 3D head shape"""
    test_df = pd.DataFrame({"x":[1]})
    # check all inputs should be the correct format
    with pytest.raises(TypeError):
        topomap_3d_head.animate_3d_head(test_df)
    with pytest.raises(TypeError):
        topomap_3d_head.animate_3d_head(raw, plot_title=0)
    with pytest.raises(TypeError):
        topomap_3d_head.animate_3d_head(raw, color_title=0)
    with pytest.raises(TypeError):
        topomap_3d_head.animate_3d_head(raw, colormap=0)
    with pytest.raises(TypeError):
        topomap_3d_head.animate_3d_head(raw, color_min="0")
    with pytest.raises(TypeError):
        topomap_3d_head.animate_3d_head(raw, color_max="0")

    # check all outpus are as expected
    ani = topomap_3d_head.animate_3d_head(raw)
    ani2 = topomap_3d_head.animate_3d_head(raw, cmin=-30, cmax=40)
    assert isinstance(ani, plotly.graph_objs._figure.Figure)
    assert ani2.data[0]['cmin'] == -30 and ani2.data[0]['cmax'] == 40

# test the topo_3d_map function
def test_topo_3d_map():
    """Test cases for plotting the static topographic map in a 3D head shape"""
    test_df = pd.DataFrame({"x":[1]})
    # check all inputs should be the correct format
    with pytest.raises(TypeError):
        topomap_3d_head.topo_3d_map(test_df)
    with pytest.raises(TypeError):
        topomap_3d_head.topo_3d_map(raw, plot_title=0)
    with pytest.raises(TypeError):
        topomap_3d_head.topo_3d_map(raw, color_title=0)
    with pytest.raises(TypeError):
        topomap_3d_head.topo_3d_map(raw, colormap=0)
    with pytest.raises(TypeError):
        topomap_3d_head.topo_3d_map(raw, color_min="0")
    with pytest.raises(TypeError):
        topomap_3d_head.topo_3d_map(raw, color_max="0")

    # check all outpus are as expected
    ani = topomap_3d_head.topo_3d_map(raw, time_stamp=0)
    ani2 = topomap_3d_head.topo_3d_map(raw, time_stamp=0, cmin=-30, cmax=40)
    assert isinstance(ani, plotly.graph_objs._figure.Figure)
    assert ani2.data[0]['cmin'] == -30 and ani2.data[0]['cmax'] == 40

    
def test_nonexistent_input_path():
    '''
    Testing input path
    '''
    with pytest.raises(FileNotFoundError):
        animate_3d_head("./srcc/999.fixica.set")

print("All tests passed")