#!/usr/bin/env python
# coding: utf-8

# # Connectivity Visualizations

# ## Connectivity Plot

# ![](instruction_imgs/connectivity.gif)

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

# ### Define parameters

# A detailed description of all parameters can be found in the `connectivity.animate_connectivity` docstring:

# In[5]:


help(connectivity.animate_connectivity)


# In[6]:


# change values below to values of interest

experiment_path = "../../data/927" # path to the experiment folder.
nth_epoch = 0

# connectivity parameters
vmin = -1
vmax = 1
colormap = "RdBu_r"
calc_type = "correlation"
pair_list = []  # select from the PAIR_OPTIONS below or use a custom pair.
line_width = None
steps = 50
threshold = 0
show_sphere = True


# In[7]:


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

# For additional options see **Creating EEG Objects** section.

# In[8]:


epochs = eeg_objects.Epochs(experiment_path)
epoch = epochs.get_nth_epoch(0)


# <br>

# ### Create the connectivity plot

# #### Generating the animation

# In[9]:


get_ipython().run_line_magic('matplotlib', 'inline')


# In[10]:


get_ipython().run_cell_magic('capture', '', '\nanim = connectivity.animate_connectivity(\n    epoch,\n    calc_type=calc_type,\n    steps=steps,\n    pair_list=pair_list,\n    threshold=threshold,\n    show_sphere=show_sphere,\n    colormap=colormap,\n    vmin=vmin,\n    vmax=vmax,\n    line_width=line_width,\n)\n\nfrom IPython.display import HTML\n\nhtml_plot = anim.to_jshtml()\nvideo = HTML(html_plot)')


# In[11]:


video


# #### Saving the animation

# ##### Save as html

# In[12]:


html_file_path = "../../exports/examples/connectivity.html"  # change the file path to where you would like to save the file

html_file = open(html_file_path, "w")
html_file.write(html_plot)
html_file.close()


# ##### Save as gif

# In[13]:


get_ipython().run_cell_magic('capture', '', '\nanim = connectivity.animate_connectivity(epoch, vmin=-1, vmax=1, pair_list=PAIR_OPTIONS["far_coherence"])\n\ngif_file_path = "../../exports/examples/connectivity.gif"  # change the file path to where you would like to save the file\nanim.save(gif_file_path, fps=3, dpi=300)  # set frames per second (fps) and resolution (dpi)')


# ##### Save as mp4

# In[14]:


mp4_file_path = "../../exports/examples/connectivity.mp4"
anim.save(mp4_file_path, fps=3, dpi=300)


# ```{note}
# If `FFMpegWriter` does not work on your computer you can save the file as a gif first and then convert it into mp4 file by running the code below.
# ```
# ```python
# import moviepy.editor as mp
# 
# clip = mp.VideoFileClip(gif_file_path)  # change the file path to where you saved the gif file
# clip.write_videofile(mp4_file_path)  # change the file path to where you would like to save the mp4 file 
# ```

# <br>

# ## Connectivity Circle Plot

# ![](instruction_imgs/connectivity_circle.gif)

# ### Define parameters

# A detailed description of all parameters can be found in the `connectivity.animate_connectivity_circle` docstring:

# In[ ]:


help(connectivity.animate_connectivity_circle)


# In[ ]:


# change values below to values of interest

# connectivity circle parameters
vmin = -1
vmax = 1
colormap = "RdBu_r"
calc_type = "correlation"
line_width = 1
steps = 50
max_connections = 50


# #### Generating the animation

# In[ ]:


get_ipython().run_line_magic('matplotlib', 'notebook')


# In[ ]:


get_ipython().run_cell_magic('capture', '', '\nanim = connectivity.animate_connectivity_circle(\n    epoch,\n    calc_type=calc_type,\n    max_connections=max_connections,\n    steps=steps,\n    colormap=colormap,\n    vmin=vmin,\n    vmax=vmax,\n    line_width=line_width,\n)\n\nfrom IPython.display import HTML\n\nhtml_plot = anim.to_jshtml()\nvideo = HTML(html_plot)')


# In[ ]:


video


# #### Saving the animation

# ##### Save as html

# In[ ]:


html_file_path = "../../exports/examples/connectivity_circle.html"  # change the file path to where you would like to save the file

html_file = open(html_file_path, "w")
html_file.write(html_plot)
html_file.close()


# ##### Save as gif

# In[ ]:


get_ipython().run_cell_magic('capture', '', '\nanim = connectivity.animate_connectivity_circle(epoch)\n\ngif_file_path = "../../exports/examples/connectivity_circle.gif"  # change the file path to where you would like to save the file\nanim.save(gif_file_path, fps=3, dpi=300) ')


# ##### Save as mp4

# In[ ]:


get_ipython().run_cell_magic('capture', '', '\nmp4_file_path = "../../exports/examples/connectivity_cicle.mp4"\nanim.save(mp4_file_path, fps=3, dpi=300)')


# ```{note}
# If `FFMpegWriter` does not work on your computer you can save the file as a gif first and then convert it into mp4 file by running the code below.
# ```
# ```python
# import moviepy.editor as mp
# 
# clip = mp.VideoFileClip(gif_file_path)  # change the file path to where you saved the gif file
# clip.write_videofile(mp4_file_path)  # change the file path to where you would like to save the mp4 file 
# ```
