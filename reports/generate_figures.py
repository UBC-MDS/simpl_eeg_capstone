from mne.io import read_raw_eeglab

example_file = "data/927/fixica.set"
raw = read_raw_eeglab(example_file)

table = raw.to_data_frame().head(10)

fig = raw.plot(duration=2)
fig.savefig("reports/images/viz_example.png")