#!/usr/bin/env python
# coding: utf-8

# # 2D Head Visualizations

# ## 2D topographic map

# ![](instruction_imgs/topo_2d.gif)

# In[1]:


from simpl_eeg import topomap_2d, eeg_objects 


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

# A detailed description of all parameters can be found in the `topomap_2d.animate_topomap_2d` docstring:

# In[5]:


help(topomap_2d.animate_topomap_2d)


# In[6]:


# change values below to values of interest

experiment_folder = "../../data/109"  # path to the experiment folder
nth_epoch = 0  # the epoch of interest
num_steps = 50 # number of steps to skip to shorten epoch

cmin = -40
cmax = 40
colormap = "Spectral"
mark = "dot"
contours = "6"
sphere = 100
res = 100
extrapolate = "head"
outlines = "head"
axes = None
mask = None
mask_params = None
colorbar = True
timestamp = True
frame_rate = 12


# <br>

# ### Create epoched data

# For additional options see **Creating EEG Objects** section.

# In[7]:


epochs = eeg_objects.Epochs(experiment_folder)
epoch = epochs.get_nth_epoch(nth_epoch)
shortened_epoch = epochs.skip_n_steps(num_steps)


# <br>

# ### Create the 2D topographic map

# #### Generating the animation

# In[8]:


get_ipython().run_cell_magic('capture', '', '\nanim = topomap_2d.animate_topomap_2d(\n    shortened_epoch,\n    colormap=colormap,\n    mark=mark,\n    contours=contours,\n    sphere=sphere,\n    cmin=cmin,\n    cmax=cmax,\n    res=res,\n    extrapolate=extrapolate,\n    outlines=outlines,\n    axes=axes,\n    mask=mask,\n    mask_params=mask_params,\n    colorbar=colorbar,\n    timestamp=timestamp,\n    frame_rate=frame_rate,\n)\n\nfrom IPython.core.display import HTML\n\nhtml_plot = anim.to_jshtml()\nvideo = HTML(html_plot)')


# In[9]:


video


# #### Saving the animation

# ##### Save as html

# In[10]:


html_file_path = "../../exports/examples/topo_2d.html"  # change the file path to where you would like to save the file

html_file = open(html_file_path, "w")
html_file.write(html_plot)
html_file.close()


# ##### Save as gif

# In[11]:


get_ipython().run_cell_magic('capture', '', '\nanim = topomap_2d.animate_topomap_2d(shortened_epoch)\n\ngif_file_path = "../../exports/examples/topo_2d.gif"  # change the file path to where you would like to save the file\nanim.save(gif_file_path, fps=5, dpi=300)')


# ##### Save as mp4

# In[12]:


get_ipython().run_cell_magic('capture', '', '\nanim = topomap_2d.animate_topomap_2d(shortened_epoch)\n\nmp4_file_path = "../../exports/examples/topo_2d.mp4"  # change the file path to where you would like to save the file\nanim.save(mp4_file_path)')


# <br>
