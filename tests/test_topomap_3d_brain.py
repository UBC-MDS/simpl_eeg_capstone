import pytest
import mne
from simpl_eeg import raw_voltage, topomap_3d_brain
import pandas as pd
import pickle
import matplotlib
import matplotlib.pyplot as plt
# from simpl_eeg_capstone import topomap_3d_brain

with open('tests/test_data/test_data1.pkl', 'rb') as input:
    epoch42 = pickle.load(input)


def test_create_fsaverage_forward():
    """Test cases for plotting 3D image mapped to the brain """
    input_epoch = epoch42

    assert type(topomap_3d_brain.create_fsaverage_forward(
        input_epoch)) == mne.forward.forward.Forward


with open('tests/test_data/test_fwd.pickle', 'rb') as input:
    input_fwd = pickle.load(input)


def test_create_inverse_solution():
    """Test cases for plotting 3D image mapped to the brain """
    input_epoch = epoch42

    assert type(
    topomap_3d_brain.create_inverse_solution(
        input_epoch,
         input_fwd)) ==  mne.source_estimate.SourceEstimate


with open('tests/test_data/test_stc.pickle', 'rb') as input:
    test_stc = pickle.load(input)

# def test_plot_topomap_3d_brain_pyvista():
#     """Test cases for plotting 3D image mapped to the brain """
#     expected_output = mne.viz._brain._brain.Brain

#     assert  type(topomap_3d_brain.plot_topomap_3d_brain(epoch42[0],
#                                   test_stc,
#                                   views = "fro",
#                                   backend = 'pyvista')) == expected_output

def test_plot_topomap_3d_brain_matplotlib():
    """Test cases for plotting 3D image mapped to the brain """
    input_epoch = epoch42
    input_stc = test_stc

    with pytest.raises(TypeError):
        topomap_3d_brain.plot_topomap_3d_brain(
    "not an epoch", input_stc, backend='matplotlib')

    with pytest.raises(TypeError):
        topomap_3d_brain.plot_topomap_3d_brain(
    input_epoch, "not an stc", 'matplotlib')

    with pytest.raises(TypeError):
        topomap_3d_brain.plot_topomap_3d_brain(input_epoch,
                                               input_stc,
                                               display_time="not a display time",
                                               backend='matplotlib')

    with pytest.raises(ValueError):
        topomap_3d_brain.plot_topomap_3d_brain(
    input_epoch, input_stc, backend = "not a valid backend")

    with pytest.raises(TypeError):
        topomap_3d_brain.plot_topomap_3d_brain(
    input_epoch, input_stc, views = 56, backend = 'matplotlib')

    with pytest.raises(ValueError):
        topomap_3d_brain.plot_topomap_3d_brain(input_epoch,
                                               input_stc,
                                               views = "not a valid view",
                                               backend = 'matplotlib')

    with pytest.raises(ValueError):
        topomap_3d_brain.plot_topomap_3d_brain(input_epoch,
                                               input_stc,
                                               backend = "matplotlib",
                                               views = "cor")  # matplotlib doesn't take 'cor'

    with pytest.raises(ValueError):
        topomap_3d_brain.plot_topomap_3d_brain(input_epoch,
                                               input_stc,
                                               views=["not a valid view",
                                                        "not a valid view 2"
                                                     ],
                                               backend = 'matplotlib')

    with pytest.raises(ValueError):
        topomap_3d_brain.plot_topomap_3d_brain(input_epoch,
                                               input_stc,
                                               backend = 'matplotlib',
                                               views = ["lat", "cor"])

    with pytest.raises(ValueError):
        topomap_3d_brain.plot_topomap_3d_brain(input_epoch,
                                               input_stc,
                                               backend = 'matplotlib',
                                               view_layout = 'not a valid layout')

    with pytest.raises(TypeError):
        topomap_3d_brain.plot_topomap_3d_brain(input_epoch,
                                               input_stc,
                                               backend = 'matplotlib',
                                               size = 'not a valid size')

    with pytest.raises(ValueError):
        topomap_3d_brain.plot_topomap_3d_brain(input_epoch,
                                               input_stc,
                                               backend = 'matplotlib',
                                               hemi = 'not a valid hemi')

    with pytest.raises(TypeError):
        topomap_3d_brain.plot_topomap_3d_brain(input_epoch,
                                               input_stc,
                                               backend = 'matplotlib',
                                               colorbar = 'not a valid hemi')

    test_single_matplotlib=topomap_3d_brain.plot_topomap_3d_brain(input_epoch,
                                                                    input_stc,
                                                                    views = "fro",
                                                                    hemi = 'lh',
                                                                    backend = 'matplotlib')

    assert type(test_single_matplotlib) == matplotlib.figure.Figure
    assert len(test_single_matplotlib.axes) == 2

    test_single_matplotlib_no_cb=topomap_3d_brain.plot_topomap_3d_brain(input_epoch,
                                                                          input_stc,
                                                                          views = "fro",
                                                                          hemi = 'lh',
                                                                          colorbar = False,
                                                                          backend = 'matplotlib')

    assert len(test_single_matplotlib_no_cb.axes) == 1
    
    test_multi_matplotlib = topomap_3d_brain.plot_topomap_3d_brain(input_epoch,
                                                                   input_stc,
                                                                   views = ['lat', 'fro'],
                                                                   hemi = 'both',
                                                                   backend = 'matplotlib',
                                                                   spacing = 'oct5')

    assert  type(test_multi_matplotlib) == matplotlib.figure.Figure 
    assert  len(test_multi_matplotlib.axes) == 6

    test_multi_matplotlib_no_cb = topomap_3d_brain.plot_topomap_3d_brain(input_epoch,
                                                                         input_stc,
                                                                         views = ['lat', 'fro'],
                                                                         hemi = 'both',
                                                                         backend = 'matplotlib',
                                                                         spacing = 'oct5',
                                                                         colorbar = False)

    assert  len(test_multi_matplotlib_no_cb.axes) == 5


def test_animate_topomap_3d_brain_matplotlib():
    """Test cases for plotting 3D image mapped to the brain """
    input_epoch = epoch42
    input_stc = test_stc
    
    with pytest.raises(TypeError):
        topomap_3d_brain.animate_matplot_brain(
                input_epoch,
                stc = test_stc,
                hemi = 'lh',
                views = ['lat'],
                timestamp = "not a timestamp"
            );
    
    with pytest.raises(TypeError):
        topomap_3d_brain.animate_matplot_brain(
                input_epoch,
                stc = test_stc,
                hemi = 'lh',
                views = ['lat'],
                frame_rate = "not a frame rate"
            );
    
    test_matplot_animate_single = topomap_3d_brain.animate_matplot_brain(
        input_epoch,
        stc = test_stc,
        hemi = 'lh',
        views = ['lat']
    );
    
    assert  type(test_matplot_animate_single) == matplotlib.animation.FuncAnimation
    
    test_matplot_animate_multi = topomap_3d_brain.animate_matplot_brain(
        input_epoch,
        stc = test_stc,
        hemi = 'both',
        views = ['lat', 'dor']
    );

    assert  type(test_matplot_animate_multi) == matplotlib.animation.FuncAnimation 
    


# def test_nonexistent_input_path():
#     '''
#     Testing input path
#     '''
#     with pytest.raises(FileNotFoundError):
#         plot_topomap_3d_brain("./srcc/999.fixica.set")


