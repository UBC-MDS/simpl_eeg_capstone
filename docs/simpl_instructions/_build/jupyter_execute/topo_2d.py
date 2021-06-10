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

experiment_folder = "../../data/109" # path to the experiment folder.
nth_epoch = 0
vmin = -40 # The minimum for the scale. Defaults to None.
vmax = 40 # The minimum for the scale. Defaults to None.
colormap = "Spectral" # select any matplotlib colormap. Defaults to RdBu_r (Red-Blue).


# <br>

# ### Create epoched data

# In[6]:


tmin = -0.5 # number of seconds before the impact
tmax = 0.5 # number of seconds after the impact
start_second = 5 # starting time of the epoch

epochs = eeg_objects.Epochs(experiment_folder, tmin, tmax, start_second)


# #### Select a specific epoch

# In[7]:


epochs.set_nth_epoch(nth_epoch)


# #### Select the number of time steps to skip (optional step)

# In[8]:


num_steps = 50
shortened_epoch = epochs.skip_n_steps(num_steps)
shortened_epoch


# #### Retrieve the selected epoch

# In[9]:


full_epoch = epochs.get_nth_epoch()
full_epoch


# <br>

# ### Create the 2D topographic map

# #### Generating the animation

# In[10]:


get_ipython().run_cell_magic('capture', '', "\nanim = topomap_2d.animate_topomap_2d(\n    shortened_epoch,\n    colormap=colormap,\n    mark='dot',\n    contours='6',\n    sphere=100,\n    cmin=vmin,\n    cmax=vmax,\n    res=100,\n    extrapolate='head',\n    outlines='head',\n    axes=None,\n    mask=None,\n    mask_params=None,\n    colorbar=True,\n    timestamp = True,\n    frame_rate=12\n)\n\nfrom IPython.core.display import HTML\nhtml_plot = anim.to_jshtml()\nvideo = HTML(html_plot)")


# In[11]:


video


# #### Saving the animation

# ##### Save as html

# In[12]:


html_file_path = "../../exports/examples/topo_2d.html"

html_file = open(html_file_path,"w")
html_file.write(html_plot)
html_file.close()


# ##### Save as gif

# In[13]:


get_ipython().run_cell_magic('capture', '', '\nanim = topomap_2d.animate_topomap_2d(shortened_epoch)\n\n# use a writer if you want to specify frames per second\nfrom matplotlib.animation import PillowWriter\nwriter = PillowWriter(fps=5)  \n\ngif_file_path = "../../exports/examples/topo_2d.gif"\nanim.save(gif_file_path, writer=writer)')


# ##### Save as mp4

# In[14]:


get_ipython().run_cell_magic('capture', '', '\nanim = topomap_2d.animate_topomap_2d(shortened_epoch)\n\nmp4_file_path = "../../exports/examples/topo_2d.mp4"\nanim.save(mp4_file_path)')


# <br>
