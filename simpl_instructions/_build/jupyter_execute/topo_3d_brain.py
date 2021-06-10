#!/usr/bin/env python
# coding: utf-8

# # 3D Brain Visualizations

# ## Topographic map in 3D brain

# ![](instruction_imgs/topomap_3d_brain.svg)

# In[1]:


from simpl_eeg import eeg_objects, topomap_3d_brain


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

# ### Create the topographic map in 3D brain

# ```{note}
# * NOTE: Before an animation or plot can be generated a "forward" and "inverse" (abbreviated as "stc") must first be generated. If they are not provided to either of the plotting animations they will be automatically generated HOWEVER this will increase the time it takes to generate the figure.
# 
# - The forward/inverse are used to retrieve a brain model to attach the EEG data to and to do some of the mapping calculations. The forward downloads 'fsaverage' MRI data which represents a brain averaged out from dozens of different patients.
# ```

# #### Generate Forward

# In[ ]:


fwd = topomap_3d_brain.create_fsaverage_forward(epoch)


# #### Generate Inverse

# In[ ]:


stc = topomap_3d_brain.create_inverse_solution(epoch, fwd)


# #### To generate figure with pyvista backend (NOT CURRENTLY WORKING)

# In[ ]:


#pyvista_brain_fig = topomap_3d_brain.plot_topomap_3d_brain(epoch, stc = stc, backend = 'pyvista')


# #### To save animation with pyvista backend (NOT CURRENTLY WORKING)

# In[ ]:


#topomap_3d_brain.save_animated_topomap_3d_brain(pyvista_brain_fig, filename = "brain_animation.gif")


# </br>

# #### To generate figure with matplotlib backend (recommended)

# In[ ]:


get_ipython().run_cell_magic('capture', '', "matplot_brain_fig = topomap_3d_brain.plot_topomap_3d_brain(epoch, stc = stc, backend = 'matplotlib')")


# ##### To save the figure

# In[ ]:


# You could change the plot to different formats by changing the format argument in the function. 
# It supports 'png', 'pdf', 'svg'.

matplot_brain_fig.savefig("topomap_3d_brain.svg", format= 'svg')


# #### To generate animation with matplotlib backend (slow but recommended)

# In[ ]:


get_ipython().run_cell_magic('capture', '', "matplotlib_animation = topomap_3d_brain.animate_matplot_brain(epoch, stc = stc, views = 'lat', hemi = 'lh')")


# ##### To save the animation as gif

# In[ ]:


from matplotlib.animation import PillowWriter
writergif = PillowWriter(fps=30)
matplotlib_animation.save("topomap_3d_brain.gif", writer=writergif)


# #### To save the animation as mp4

# You would need to save it as gif file first and then convert it into mp4 file.

# In[ ]:


import moviepy.editor as mp

clip = mp.VideoFileClip("topomap_3d_brain.gif")
clip.write_videofile("topomap_3d_brain.mp4") 


# <br>
