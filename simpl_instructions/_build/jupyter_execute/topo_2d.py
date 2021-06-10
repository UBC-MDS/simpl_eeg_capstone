#!/usr/bin/env python
# coding: utf-8

# # 2D Head Visualizations

# ## 2D topographic map

# ![](instruction_imgs/topo_2d.gif)

# In[1]:


from simpl_eeg import eeg_objects, topomap_2d


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

# ### Create the 2D topographic map

# #### To generate the animation

# In[ ]:


get_ipython().run_cell_magic('capture', '', "topo_2d = topomap_2d.animate_topomap_2d(epoch,\n                       colormap=colormap,\n                       mark='dot',\n                       contours='6',\n                       sphere=100,\n                       cmin= vmin,\n                       cmax = vmin,\n                       res=100,\n                       extrapolate='head',\n                       outlines='head',\n                       axes=None,\n                       mask=None,\n                       mask_params=None,\n                       colorbar=True,\n                       timestamp = True,\n                       frame_rate=12)")


# In[ ]:


from IPython.display import HTML

HTML(topo_2d.to_jshtml())


# #### To save the animation

# ##### To save the animation as gif

# In[ ]:


from matplotlib.animation import PillowWriter
writergif = PillowWriter(fps=30)
topo_2d.save("topo_2d.gif", writer=writergif)


# ##### To save the animation as mp4

# You would need to save it as gif file first and then convert it into mp4 file.

# In[ ]:


import moviepy.editor as mp

clip = mp.VideoFileClip("topo_2d.gif")
clip.write_videofile("topo_2d.mp4") 


# <br>

# In[ ]:




