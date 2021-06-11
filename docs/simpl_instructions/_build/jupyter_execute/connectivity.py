#!/usr/bin/env python
# coding: utf-8

# # Connectivity Visualizations

# ## Connectivity Plot

# <img src="instruction_imgs/connectivity.gif" align="left" style="height:30em"/>

# In[1]:


from simpl_eeg import connectivity, eeg_objects


# In[2]:


import warnings
warnings.filterwarnings('ignore')


# ```{note}
# Please include the line below in your IDE so that the changes would be simultaneously reflected when you make a change to the python scripts.**
# ```

# In[3]:


get_ipython().run_line_magic('load_ext', 'autoreload')


# In[4]:


get_ipython().run_line_magic('autoreload', '2')


# <br>

# ### Define global parameters

# There are some common parameters for all functions in this package, it would be more convenient to define all parameters before going into each functions.

# In[5]:


# change values below to values of interest

experiment_path = "../../data/927" # path to the experiment folder.
nth_epoch = 0
vmin = -1 # The minimum for the scale. Defaults to None.
vmax = 1 # The minimum for the scale. Defaults to None.
colormap = 'RdBu_r' # select from ["RdBu_r", "hot", "cool", "inferno", "turbo", "rainbow"]. Defaults to 'RdBu_r'.
calc_type = 'correlation' # select from ["correlation", "spectral_connectivity","envelope_correlation"]
pair_list = "all_pairs" # select from the PAIR_OPTIONS below
line_width = None # The line width for the connections. Defaults to None for non-static width.
max_connections = 50 # Number of connections to display. Defaults to 50.


# In[6]:


PAIR_OPTIONS = {
    "all_pairs": [],
    "local_anterior": "Fp1-F7, Fp2-F8, F7-C3, F4-C4, C4-F8, F3-C3",
    "local_posterior": "T5-C3, T5-O1, C3-P3, C4-P4, C4-T6, T6-O2",
    "far_coherence": "Fp1-T5, Fp2-T6, F7-T5, F7-P3, F7-O1, T5-F3, F3-P3, F4-P4, P4-F8, F8-T6, F8-O2, F4-T6",
    "prefrontal_to_frontal_and_central": "Fp1-F3, Fp1-C3, Fp2-F4, Fp2-C4",
    "occipital_to_parietal_and_central": "C3-O1, P3-O1, C4-O2, P4-O4",
    "prefrontal_to_parietal": "Fp1-P3, Fp2-P4",
    "frontal_to_occipital": "F3-O1, P4-O2",
    "prefrontal_to_occipital": "Fp1-O1, Fp2-O2"
}


# <br>

# ### Create epoched data

# In[7]:


epochs = eeg_objects.Epochs(experiment_path)
epoch = epochs.get_nth_epoch(0)


# <br>

# ### Create the connectivity plot

# #### Generating the animation

# In[8]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[9]:


get_ipython().run_cell_magic('capture', '', '\nconn_plot_animated = connectivity.animate_connectivity(\n    epoch,\n    calc_type=calc_type,\n    steps=20,\n    pair_list=pair_list,\n    threshold=0,\n    show_sphere=True,\n    colormap=colormap,\n    vmin=vmin,\n    vmax=vmax,\n    line_width=line_width,\n)\n\nfrom IPython.display import HTML\n\nconn_html = conn_plot_animated.to_jshtml()\nconn_video = HTML(conn_html)')


# #### Saving the animation

# ##### Save as html

# In[10]:


html_file_path = "../../exports/examples/connectivity.html"  # change the file path to where you would like to save the file

html_file = open(html_file_path, "w")
html_file.write(conn_html)
html_file.close()


# ##### Save as gif

# In[11]:


get_ipython().run_cell_magic('capture', '', '\nanim_conn = connectivity.animate_connectivity(epoch, vmin=-1, vmax=1, pair_list=PAIR_OPTIONS["far_coherence"])\n\nconn_gif_file_path = "../../exports/examples/connectivity.gif"  # change the file path to where you would like to save the file\nanim_conn.save(conn_gif_file_path, fps=3, dpi=300)  # set frames per second (fps) and resolution (dpi)')


# ##### Save as mp4

# In[12]:


conn_mp4_file_path = "../../exports/examples/connectivity.mp4"
anim_conn.save(conn_mp4_file_path, fps=3, dpi=300)


# ```{note}
# If `FFMpegWriter` does not work on your computer you can save the file as a gif first and then convert it into mp4 file.
# ```

# In[13]:


import moviepy.editor as mp

clip = mp.VideoFileClip(conn_gif_file_path) # change the file path to where you saved the gif file
clip.write_videofile(conn_mp4_file_path) # change the file path to where you would like to save the file


# <br>

# ## Connectivity Circle Plot

# <img src="instruction_imgs/connectivity_circle.gif" align="left" style="height:30em"/>

# #### Generating the animation

# In[14]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[15]:


get_ipython().run_cell_magic('capture', '', '\nplot_cir_animated = connectivity.animate_connectivity_circle(\n    epoch,\n    calc_type=calc_type,\n    max_connections=max_connections,\n    steps=50,\n    colormap=colormap,\n    vmin=vmin,\n    vmax=vmax,\n    line_width=line_width,\n)\n\nfrom IPython.display import HTML\n\ncir_html = plot_cir_animated.to_jshtml()\ncir_video = HTML(cir_html)')


# In[ ]:


cir_video


# #### Saving the animation

# ##### Save as html

# In[ ]:


cir_html_file_path = "../../exports/examples/connectivity_circle.html"  # change the file path to where you would like to save the file

cir_html_file = open(cir_html_file_path, "w")
cir_html_file.write(cir_html)
cir_html_file.close()


# ##### Save as gif

# In[ ]:


get_ipython().run_cell_magic('capture', '', '\nanim_cir = connectivity.animate_connectivity_circle(epoch)\n\ncir_gif_file_path = "../../exports/examples/connectivity_circle.gif"  # change the file path to where you would like to save the file\nanim_cir.save(cir_gif_file_path, fps=3, dpi=300) ')


# ##### Save as mp4

# In[ ]:


get_ipython().run_cell_magic('capture', '', '\ncir_mp4_file_path = "../../exports/examples/connectivity_cicle.mp4"\nanim_cir.save(cir_mp4_file_path, fps=3, dpi=300)')


# ```{note}
# If `FFMpegWriter` does not work on your computer you can save the file as a gif first and then convert it into mp4 file.
# ```

# In[ ]:


import moviepy.editor as mp

clip = mp.VideoFileClip(cir_gif_file_path) # change the file path to where you saved the gif file
clip.write_videofile(cir_mp4_file_path) # change the file path to where you would like to save the file 

