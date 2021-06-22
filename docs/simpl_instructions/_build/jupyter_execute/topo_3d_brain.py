#!/usr/bin/env python
# coding: utf-8

# # 3D Brain Visualizations

# ## 3D topographic brain map
# 
# The 3D topographic brain map provides a view of voltage measurements as a heatmap converted to estimated position on the brain. There are 2 plot options with different backends: 
# 
# 1) [matplotlib](#matplotlib) (the version found on the UI)
# 
# 2) [pyVista](#pyvista) (a better rendering but incompatible with the UI)
# 
# Both plots can be generated as an animation to view changes over time or as a standalone plot.

# ![](instruction_imgs/presentattion_brain.gif)

# ## General Setup
# ### Import required modules

# In[1]:


from simpl_eeg import topomap_3d_brain, eeg_objects


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


experiment_folder = "../../data/109"
epochs = eeg_objects.Epochs(experiment_folder)

frame_steps = 100
epoch = epochs.skip_n_steps(frame_steps)


# ### Generate forward and inverse (optional)

# ```{note}
# - Before an animation or plot can be generated, a **"forward"** and **"inverse"** (abbreviated as **"stc"**) must first be generated. If they are not provided to either of the plotting animations they will be automatically generated, **HOWEVER** this will increase the time it takes to generate the figure.
# 
# - The forward/inverse are used to retrieve a brain model to attach the EEG data and to do some of the mapping calculations. The forward downloads 'fsaverage' MRI data which represents a brain averaged out from dozens of different patients.
# ```

# #### Generate Forward

# In[6]:


fwd = topomap_3d_brain.create_fsaverage_forward(epoch)


# #### Generate Inverse

# In[7]:


stc = topomap_3d_brain.create_inverse_solution(epoch, fwd)


# <a id="matplotlib"></a>
# ## Create a matplotlib 3D brain animation (recommended)

# ### Define parameters

# A detailed description of all parameters can be found in the `topomap_3d_brain.animate_matplot_brain` docstring:

# In[8]:


help(topomap_3d_brain.animate_matplot_brain)


# In[9]:


colormap = "RdBu_r"


# #### Generate animation with matplotlib backend (slow but recommended)

# In[10]:


get_ipython().run_cell_magic('capture', '', "\nmatplotlib_animation = topomap_3d_brain.animate_matplot_brain(epoch, stc = stc, views = 'lat', hemi = 'lh')\n\nfrom IPython.display import HTML\nvideo = HTML(matplotlib_animation.to_jshtml())")


# In[11]:


video


# ### Saving the animation

# #### Save as gif

# ```python
# anim_brain = topomap_3d_brain.animate_matplot_brain(epoch, stc = stc, views = 'lat', hemi = 'lh')
# 
# gif_file_path = "examples/topomap_3d_brain.gif" 
# anim_brain.save(gif_file_path, fps=5, dpi=300)
# ```

# #### Save as mp4

# ```python
# mp4_file_path = "examples/topo_2d.mp4"
# anim_brain.save(mp4_file_path, fps=5, dpi=300)
# ```

# ```{note}
# If `FFMpegWriter` does not work on your computer you can save the file as a gif first and then convert it into mp4 file by running the code below.
# ```
# ```python
# import moviepy.editor as mp
# 
# clip = mp.VideoFileClip(gif_file_path)
# clip.write_videofile(mp4_file_path)
# ```

# ## Create a matplotlib 3D brain figure

# ### Generating a matplotlib plot

# In[12]:


get_ipython().run_cell_magic('capture', '', "matplot_brain_fig = topomap_3d_brain.plot_topomap_3d_brain(epoch, stc=stc, backend='matplotlib')")


# ### Save the plot
# You can change the file to different formats by changing the format argument in the function. It supports `png`, `pdf`, `svg`.
# ```python
# file_path = "examples/topomap_3d_brain.svg"  
# matplot_brain_fig.savefig(file_path, format='svg')
# ```

# <a id="pyvista"></a>
# ## Create a pyVista 3D brain animation

# ### Generate figure with pyvista backend

# ```python
# pyvista_brain_fig = topomap_3d_brain.plot_topomap_3d_brain(epoch, stc = stc, backend = 'pyvista')
# ```

# ### Save animation with pyvista backend

# ```python
# topomap_3d_brain.save_animated_topomap_3d_brain(pyvista_brain_fig, filename = "brain_animation.gif")
# ```
