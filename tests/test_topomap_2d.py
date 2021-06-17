import pytest
import pickle
import matplotlib
import matplotlib.pyplot as plt
from simpl_eeg import topomap_2d

# import the test data
with open('tests/test_data/test_data.pkl', 'rb') as input:
    EPOCH_1 = pickle.load(input)
with open('tests/test_data/test_data1.pkl', 'rb') as input:
    EPOCH_42 = pickle.load(input)


def test_plot_topomap_2d():
    """Test standalone plot"""

    output_fig = topomap_2d.plot_topomap_2d(EPOCH_42)
    assert isinstance(output_fig, matplotlib.image.AxesImage)


def test_animate_topomap_2d():
    """Test animated plot"""

    output_ani = topomap_2d.animate_topomap_2d(EPOCH_42)
    assert isinstance(output_ani, matplotlib.animation.FuncAnimation)


def test_add_timestamp():
    """Test add timestamp"""

    expected_text = "time:  0.0000s"

    topomap_2d.plot_topomap_2d(EPOCH_1)
    topomap_2d.add_timestamp(EPOCH_1, 0, 1, 1)

    text_found = False

    for child in plt.gca().get_children():
        if isinstance(child, matplotlib.text.Text):
            if child.get_text() == expected_text:
                text_found = True

    assert text_found is True


if __name__ == '__main__':
    test_add_timestamp()
    test_plot_topomap_2d()
    test_animate_topomap_2d()
    print("All tests passed!")
