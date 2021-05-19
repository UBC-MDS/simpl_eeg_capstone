from mne.connectivity import spectral_connectivity
from mne.viz import circular_layout, plot_connectivity_circle
import matplotlib.animation as animation

PAIR_OPTIONS = {
    all_pairs : []
    local_anterior : "Fp1-F7, Fp2-F8, F7-C3, F4-C4, C4-F8, F3-C3",
    local_posterior : "T5-C3, T5-O1, C3-P3, C4-P4, C4-T6, T6-O2",
    far_coherence : "Fp1-T5, Fp2-T6, F7-T5, F7-P3, F7-O1, T5-F3, F3-P3, F4-P4, P4-F8, F8-T6, F8-O2, F4-T6",
    prefrontal_to_frontal_and_central : "Fp1-F3, Fp1-C3, Fp2-F4, Fp2-C4",
    occipital_to_parietal_and_central : "C3-O1, P3-O1, C4-O2, P4-O4",
    prefrontal_to_parietal : "Fp1-P3, Fp2-P4",
    frontal_to_occipital : "F3-O1, P4-O2",
    prefrontal_to_occipital : "Fp1-O1, Fp2-O2"
}

def convert_pairs(string_pairs):
    tuple_pairs = string_pairs
    if type(string_pairs) == str:
        pairs = string_pairs.split(", ")
        tuple_pairs = [tuple(pair.split("-")) for pair in pairs]
    return tuple_pairs
    
def calculate_connectivity(data, calc_type="correlation"):
    conn_df = data.to_data_frame().corr()
    if calc_type == "spectral_connectivity":
        conn = mne.connectivity.spectral_connectivity(
            data, method="pli", mode="fourier", faverage=True, verbose=False
        )[0][:,:,0]
    elif calc_type == "envelope_correlation":
        conn = mne.connectivity.envelope_correlation(data)
    elif calc_type == "covariance":
        conn = mne.compute_covariance(data, verbose=False).data
        
    if calc_type != "correlation":
        conn_df.iloc[-conn.shape[0]:, -conn.shape[1]:] = conn
    return conn_df

def plot_connectivity(fig, data, locations, pair_list=[], threshold=0, calc_type="correlation"):
    correlation_df = calculate_connectivity(data, calc_type)
    possible_colours = plt.cm.rainbow(correlation_df)

    ax = fig.add_subplot()
    node_df = pd.DataFrame(
        {
            "name": [node.get_text() for node in locations],
            "x": [node.get_position()[0] for node in locations],
            "y": [node.get_position()[1] for node in locations],
        }
    )
    x_list = []
    y_list = []

    for x1, y1, name1 in zip(node_df["x"], node_df["y"], node_df["name"]):
        for x2, y2, name2 in zip(node_df["x"], node_df["y"], node_df["name"]):
            if (name1, name2) in pair_list or not pair_list:
                correlation = correlation_df.loc[name1, name2]
                if abs(correlation) >= threshold:
                    row = correlation_df.columns.get_loc(name1)
                    col = correlation_df.index.get_loc(name2)
                    x_list = [x1, x2]
                    y_list = [y1, y2]
                    ax.plot(
                        x_list,
                        y_list,
                        color=possible_colours[row, col],
                        linewidth=0.2/(1-correlation),
                    )
    fig.colorbar(plt.cm.ScalarMappable(cmap="rainbow"))
    raw.plot_sensors(axes=ax, show_names=True, ch_groups="selection", kind="topomap")
    return fig

def animate_connectivity(epochs, calc_type="correlation", pair_list=[]):
    pair_list = convert_pairs(pair_list)

    fig = plt.figure()
    def animate(frame_number):
        fig.clear()
        return [plot_connectivity(fig, epochs[frame_number], locations, pair_list=pair_list, threshold=0, calc_type=calc_type)]
    anim = animation.FuncAnimation(fig, animate, len(epochs), blit=True)
    return anim

def plot_conn_circle(data, fig, calc_type="correlation", max_connections=50, channel_names=[]):
    if not channel_names: 
        channel_names = data.ch_names
    conn = calculate_connectivity(data, calc_type=calc_type).loc[channel_names, channel_names].to_numpy()
    mne.viz.plot_connectivity_circle(
        conn,
        channel_names,
        n_lines=max_connections,
        fig=fig,
        node_angles=circular_layout(channel_names, channel_names, start_pos=90), 
    )[0]
    return fig

def animate_connectivity_circle(epochs, calc_type="correlation"):
    fig = plt.figure()
    def animate(frame_number):
        fig.clear()
        return [plot_conn_circle(epochs[frame_number], fig, calc_type=calc_type)];

    anim = animation.FuncAnimation(fig, animate_connectivity_circle, len(epochs), blit=True)
    return anim
