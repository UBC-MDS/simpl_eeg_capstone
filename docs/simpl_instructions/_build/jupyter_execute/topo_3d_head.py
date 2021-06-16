#!/usr/bin/env python
# coding: utf-8

# # 3D Head Visualizations

# ## 3D topographic head map
# 
# The 3D topographic head map provides a view of voltage measurements as a heatmap imposed on a 3D skull shape. It can be generated as an [animation](#animation) to view changes over time or as a [standalone plot](#plot). 

# ![](instruction_imgs/topo_3d_head_ani.gif)

# ## General Setup
# ### Import required modules

# In[1]:


from simpl_eeg import topomap_3d_head, eeg_objects


# In[2]:


import warnings
warnings.filterwarnings('ignore')


# ```{note}
# Please include the line below in your IDE so that the changes would be simultaneously reflected when you make a change to the python scripts.
# ```

# In[3]:


get_ipython().run_line_magic('load_ext', 'autoreload')


# In[4]:


get_ipython().run_line_magic('autoreload', '2')


# ### Create epoched data
# For additional options see [Creating EEG Objects](eeg_objects.html#intro) section.

# In[5]:


experiment_folder = "../../data/927"
nth_epoch = 0

epochs = eeg_objects.Epochs(experiment_folder)
epoch = epochs.get_nth_epoch(nth_epoch)


# <a id="animation"></a>
# ## Create a 3D topographic animation

# ### Define parameters

# A detailed description of all parameters can be found in the `topomap_3d_head.animate_3d_head` docstring:

# In[6]:


help(topomap_3d_head.animate_3d_head)


# In[7]:


color_min = -40
color_max = 40
colormap = "RdBu_r"
time_stamp = -300


# #### Generating the animation

# In[8]:


topo_3d_head = topomap_3d_head.animate_3d_head(
    epoch,
    color_title="EEG MicroVolt",
    color_min=color_min,
    color_max=color_max,
    colormap=colormap,
)


# In[9]:


topo_3d_head.show()


# ### Saving the animation

# #### Save as html

# ```python
# html_file_path = "examples/topo_3d.html"
# topo_3d_head.write_html(html_file_path)
# ```

# #### Save as gif

# ```python
# topomap_3d_head.save_gif(epoch, gifname="topo_3d_head_ani", duration=200)
# ```

# #### Save as mp4 

# ```{note}
# You need to save the file as gif first and then convert it into mp4 file.
# ```

# ```python
# import moviepy.editor as mp
# 
# clip = mp.VideoFileClip("topo_3d_head_ani.gif")
# clip.write_videofile("examples/topo_3d_head_ani.mp4")
# ```

# <a id="plot"></a>
# ## Create a 3D topographic plot

# ### Define parameters
# A detailed description of all animation parameters can be found in the `topomap_2d.topo_3d_map` docstring:

# In[10]:


help(topomap_3d_head.topo_3d_map)


# In[11]:


topo_3d__head_static = topomap_3d_head.topo_3d_map(
    epoch,
    time_stamp,
    color_title="EEG MicroVolt",
    color_min=color_min,
    color_max=color_max,
    colormap=colormap,
)


# In[12]:


topo_3d__head_static.show()


# ### Saving the plot
# You can change the plot to different formats by changing the format argument in the function. It supports 'png', 'pdf', 'svg'.

# #### Save as svg
# ```python
# static_file_path = "examples/topo_3d_static.svg"
# topo_3d__head_static.write_image(static_file_path, engine="kaleido")
# ```

# #### Save as png
# ```python
# static_file_path_png = "examples/topo_3d_static.png"
# 
# # no need to specify engine if not saving as svg file
# topo_3d__head_static.write_image(static_file_path_png)
# ```
