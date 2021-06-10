#!/usr/bin/env python
# coding: utf-8

# # Connectivity Visualizations

# ## Connectivity Plot

# ![](instruction_imgs/connectivity.gif)

# In[1]:


from simpl_eeg import eeg_objects, connectivity


# In[2]:


import warnings
warnings.filterwarnings('ignore')


# **Please include the line below in your IDE so that the changes would be simultaneously reflected when you make a change to the python scripts.**

# In[3]:


get_ipython().run_line_magic('load_ext', 'autoreload')


# In[4]:


get_ipython().run_line_magic('autoreload', '2')


# <br>

# ### Define global parameters

# There are some common parameters for all functions in this package, it would be more convenient to define all parameters before going into each functions.

# In[5]:


# change None to values of interest

experiment = None # has to be a string
nth_epoch = None
vmin = None # The minimum for the scale. Defaults to None.
vmax = None # The minimum for the scale. Defaults to None.
colormap = None # select from ["RdBu_r", "hot", "cool", "inferno", "turbo", "rainbow"]
calc_type = None # select from ["correlation", "spectral_connectivity","envelope_correlation"]
pair_list = None # select from the PAIR_OPTIONS below
line_width = None # The line width for the connections. Defaults to None for non-static width.
max_connections = None # Number of connections to display. Defaults to 50.


# ```python
# PAIR_OPTIONS = {
#     "all_pairs": [],
#     "local_anterior": "Fp1-F7, Fp2-F8, F7-C3, F4-C4, C4-F8, F3-C3",
#     "local_posterior": "T5-C3, T5-O1, C3-P3, C4-P4, C4-T6, T6-O2",
#     "far_coherence": "Fp1-T5, Fp2-T6, F7-T5, F7-P3, F7-O1, T5-F3, F3-P3, F4-P4, P4-F8, F8-T6, F8-O2, F4-T6",
#     "prefrontal_to_frontal_and_central": "Fp1-F3, Fp1-C3, Fp2-F4, Fp2-C4",
#     "occipital_to_parietal_and_central": "C3-O1, P3-O1, C4-O2, P4-O4",
#     "prefrontal_to_parietal": "Fp1-P3, Fp2-P4",
#     "frontal_to_occipital": "F3-O1, P4-O2",
#     "prefrontal_to_occipital": "Fp1-O1, Fp2-O2"
# }
# ```

# <br>

# ### Create epoched data

# In[6]:


tmin = None # number of seconds before the impact
tmax = None # number of seconds after the impact
start_second = None # starting time of the epoch

raw = eeg_objects.Epochs(experiment, tmin, tmax, start_second)


# #### To select the epoch

# In[ ]:


raw.set_nth_epoch(nth_epoch)


# #### To select the number of time steps to skip (optional step)

# In[ ]:


raw.skip_n_steps(num_steps)


# #### To get the selected epoch

# In[ ]:


epoch = raw.get_nth_epoch()


# <br>

# ### Create the connectivity plot

# #### To generate the animtation

# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


get_ipython().run_cell_magic('capture', '', 'conn_plot_animated = connectivity.animate_connectivity(epoch,\n    calc_type=calc_type,\n    steps=20,\n    pair_list=pair_list,\n    threshold=0,\n    show_sphere=True,\n    colormap=colormap,\n    vmin=vmin,\n    vmax=vmax,\n    line_width=line_width)')


# In[ ]:


from IPython.display import HTML

HTML(conn_plot_animated.to_jshtml())


# #### To save the animattion

# ##### To save the animated plot as gif

# In[ ]:


from matplotlib.animation import PillowWriter
writergif = PillowWriter(fps=30)
conn_plot_animated.save("connectivity.gif", writer=writergif)


# ##### To save the animated plot as mp4

# You would need to save it as gif file first and then convert it into mp4 file.

# In[ ]:


import moviepy.editor as mp

clip = mp.VideoFileClip("connectivity.gif")
clip.write_videofile("connectivity.mp4")


# <br>

# ### Create the connectivity cicle plot

# #### To generate the animtation

# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


get_ipython().run_cell_magic('capture', '', 'conn_plot_cir_animated = connectivity.animate_connectivity_circle(epoch,\n    calc_type=calc_type,\n    max_connections=max_connections,\n    steps=20,\n    colormap=colormap,\n    vmin=vmin,\n    vmax=vmax,\n    line_width=line_width)')


# In[ ]:


from IPython.display import HTML

HTML(conn_plot_cir_animated.to_jshtml())


# #### To save the animattion

# ##### To save the animated plot as gif

# In[ ]:


from matplotlib.animation import PillowWriter
writergif = PillowWriter(fps=30)
conn_plot_cir_animated.save("connectivity_cicle.gif", writer=writergif)


# ##### To save the animated plot as mp4

# You would need to save it as gif file first and then convert it into mp4 file.

# In[ ]:


import moviepy.editor as mp

clip = mp.VideoFileClip("connectivity_cicle.gif")
clip.write_videofile("connectivity_cicle.mp4")


# In[ ]:




