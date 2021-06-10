#!/usr/bin/env python
# coding: utf-8

# # `simpl_eeg` package

# ##  Topographic map in 3D head

# ![](instruction_imgs/topo_3d_head_ani.gif)

# In[1]:


from simpl_eeg import eeg_objects, topomap_3d_head


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
color_min = None
color_max = None
colormap = None # select from ["RdBu_r", "hot", "cool", "inferno", "turbo", "rainbow"]


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


# </br>

# ### Create the topographic map in 3D head shape

# In[ ]:


timestamp = -300 # you can change the value to the time stamp of your interest
topo_3d__head_static = topomap_3d_head.topo_3d_map(epoch, time_stamp,  color_title="EEG MicroVolt",  color_min = color_min, color_max = color_max, colormap=colormap)


# In[ ]:


topo_3d__head_static.show()


# #### To generate the animnation

# In[ ]:


topo_3d_head = topomap_3d_head.animate_3d_head(epoch, color_title="EEG MicroVolt", color_min = color_min, color_max = color_max, colormap=colormap)


# In[ ]:


topo_3d_head.show()


# #### To save the animnation

# ##### To save the static plot

# In[ ]:


topo_3d__head_static.write_image("topo_3d_static.svg", engine="kaleido") 


# In[ ]:


topo_3d__head_static.write_image("topo_3d_static.png") # no need to specify engine if not saved as svg file


# ##### To save the animnation as html

# In[ ]:


topo_3d_head.write_html("topo_3d.html")


# ##### To save the animation as gif file

# In[ ]:


topomap_3d_head.save_gif(epoch, gifname="topo_3d_head_ani", duration=200)


# ##### To save the animation as mp4 file

# You would need to save it as gif file first and then convert it into mp4 file.

# In[ ]:


import moviepy.editor as mp

clip = mp.VideoFileClip("topo_3d_head_ani.gif")
clip.write_videofile("topo_3d_head_ani.mp4")


# In[ ]:




