import matplotlib.pyplot as plt
import matplotlib.animation as animation
import mne
import numpy as np
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable


def plot_topomap_2d(epoch, frame_number, colormap='RdBu_r', plot_epoch_number=0,
    mark='dot', contours='6', sphere=100, mu_v_min=-10, mu_v_max=10, res=100,
    extrapolate='head', outlines='head', axes=None, mask=None, mask_params=None,
    ):

    # if epoch data is passed then extract a specific epoch number 
    # and convert it to the same format as evoked data
    if type(epoch) == mne.epochs.Epochs:
        plotting_data = epoch[plot_epoch_number].get_data()[0]
    elif type(epoch) == mne.evoked.EvokedArray:
        plotting_data = epoch

    if mark == 'dot':
        sensor_value = True
        names_value = False
        show_names_value = False
    if mark == 'r+':
        sensor_value = 'r+'
        names_value = False
        show_names_value = False
    if mark == 'channel_name':
        sensor_value = True
        names_value = epoch.ch_names
        show_names_value = True
    if mark == 'none':
        sensor_value = False
        names_value = False
        show_names_value = False

    topo_2d_fig = mne.viz.plot_topomap(
        data=plotting_data[:, frame_number],
        pos=epoch.info,  # Location info for data points
        show=False,
        #vmin=vmin_mu_V_2d/1e6,  # Convert back to volts
        #vmax=vmax_mu_V_2d/1e6,
        sphere=sphere,  # Causes head to appear, see documentation, not sure what value should be here so 100 is placeholder
        outlines=outlines,  # 'head' keeps signals within head space, 'skirt' extrapolates beyond PROBS LEAVE ON 'head'
        extrapolate=extrapolate,  # 'local' is off-center. PROBS LEAVE ALWAYS ON 'head'
        res=res,  # n x n pixels in the actual waves MAYBE USEFUL
        cmap=colormap,  # RdBu_r seems to be the standard PROBS USEFUL
        sensors=sensor_value,  # True=black dots, "r+"=red + MAYBE USEFUL
        axes=None,  # used if you're plotting multiple images PROBS NOT USEFUL
        names=names_value,  # Feed in channel names MAYBE USEFUL
        show_names=show_names_value,  # Show channel names at each location MAYBE USEFUL
        mask=mask,  # Marks siginficant points/times if that's wanted PROBABLY NOT USEFUL
        mask_params=None,  # PROBABLY NOT USEFUL
        contours=contours,  # Number of lines that divide up sections to be drawn MAYBE USEFUL
    )[0]

    return topo_2d_fig

def animate_topomap_2d(epoch, colormap='RdBu_r', plot_epoch_number=0,
    mark='dot', contours='6', sphere=100, mu_v_min=-10, mu_v_max=10, res=100,
    extrapolate='head', outlines='head', axes=None, mask=None, mask_params=None,
    colorbar=True, show_every_nth_frame=3, frame_rate=12):

    # Generate array of all frames to be shown based on parameters
    if type(epoch) == mne.epochs.Epochs:
        frames_to_show = np.arange(0, epoch[0].get_data()[0].shape[1], show_every_nth_frame)
    elif type(epoch) == mne.evoked.EvokedArray:
        frames_to_show = np.arange(0, evoked.data.shape[1], show_every_nth_frame)

    ms_between_frames = 1000/frame_rate

    fig, ax = plt.subplots()

    def animate(frame_number):
        fig.clear()
        # https://mne.tools/dev/generated/mne.viz.plot_topomap.html
        topomap_2d = plot_topomap_2d(
            epoch=epoch,
            frame_number=frame_number,
            colormap=colormap,
            plot_epoch_number=plot_epoch_number,
            mark=mark,
            contours=contours,
            sphere=sphere,
            mu_v_min=mu_v_min,
            mu_v_max=mu_v_max,
            res=res,
            extrapolate=extrapolate,
            outlines=outlines,
            axes=ax,
            mask=mask,
            mask_params=mask_params
        )

        # Consider changing to screenshot of colorbar genearted at the start to increase calculation speed
        if colorbar == True:
            ax_divider = make_axes_locatable(ax)
            cax = ax_divider.append_axes("right", size="2%", pad="0%")
            clim = dict(kind='value', lims=[mu_v_min, 0, mu_v_max])  # CHECK
            # https://mne.tools/stable/generated/mne.viz.plot_brain_colorbar.html
            mne.viz.plot_brain_colorbar(
                cax,
                clim,
                #colormap=topomap_2d.get_cmap().name,  # get same cmap that's in the 2D topomap
                transparent=False,
                orientation='vertical',
                label='µV',
                bgcolor='0'
            )
        return [fig]

    ani = animation.FuncAnimation(
        fig,
        animate,
        frames=frames_to_show,
        interval=ms_between_frames,  # Time between frames in ms
        blit=True
    )

    return ani
