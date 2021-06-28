"""
Python script for generating report and figures
"""

import matplotlib
matplotlib.use("Agg")

from simpl_eeg import (
    eeg_objects,
    raw_voltage,
    connectivity,
    topomap_2d,
    topomap_3d_brain,
    topomap_3d_head
)

example_path = "data/927"
epochs = eeg_objects.Epochs(example_path)
epoch = epochs.epoch
raw = epochs.eeg_file.raw

table = raw.to_data_frame().head(10)

fig = raw.plot(duration=2)
fig.savefig("reports/images/viz_example.png")

fig = raw_voltage.plot_voltage(epoch, remove_xlabel=True, width=5, height=3, show_scrollbars=False)
fig.savefig("reports/images/raw_voltage.png")

fig = topomap_2d.plot_topomap_2d(epoch)
fig.figure.savefig("reports/images/2d_head.png")

fig = topomap_3d_head.topo_3d_map(epoch, 0)
fig.write_image("reports/images/3d_head.png")

fig = topomap_3d_brain.plot_topomap_3d_brain(epoch, views=['lat','dor'], hemi='both', cmin=-1.5, cmax=1.5)
fig.savefig("reports/images/3d_brain.png")

fig = connectivity.plot_connectivity(epoch)
fig.savefig("reports/images/connectivity.png")

fig = connectivity.plot_conn_circle(epoch)
fig.savefig("reports/images/connectivity_circle.png")

fig = raw.plot(duration=2, n_channels=5, show_options=False, show_scrollbars=False, show_scalebars=False)
fig.set_size_inches(3, 1.5)
fig.savefig("reports/images/viz_example2.png")