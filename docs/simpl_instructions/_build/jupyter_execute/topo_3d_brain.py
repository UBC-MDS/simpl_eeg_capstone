#!/usr/bin/env python
# coding: utf-8

# # 3D Brain Visualizations

# ## Topographic map in 3D brain

# ![](instruction_imgs/topomap_3d_brain.gif)

# In[1]:


from simpl_eeg import eeg_objects, topomap_3d_brain


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


# <br>

# ### Define parameters

# A detailed description of all parameters can be found in the `topomap_2d.animate_topomap_2d` docstring:

# In[5]:


help(topomap_3d_brain.animate_matplot_brain)


# In[6]:


# change values belo to values of interest

experiment_folder = "../../data/109"  # path to the experiment folder
nth_epoch = 0  # the epoch of interest

# 3D brain parameters
colormap = "RdBu_r"


# <br>

# ### Create epoched data

# For additional options see **Creating EEG Objects** section.

# In[7]:


epochs = eeg_objects.Epochs(experiment_folder)
epoch = epochs.get_nth_epoch(nth_epoch)


# </br>

# ### Create the topographic map in 3D brain

# ```{note}
# - Before an animation or plot can be generated a **"forward"** and **"inverse"** (abbreviated as **"stc"**) must first be generated. If they are not provided to either of the plotting animations they will be automatically generated **HOWEVER** this will increase the time it takes to generate the figure.
# 
# - The forward/inverse are used to retrieve a brain model to attach the EEG data to and to do some of the mapping calculations. The forward downloads 'fsaverage' MRI data which represents a brain averaged out from dozens of different patients.
# ```

# #### Generate Forward

# In[8]:


fwd = topomap_3d_brain.create_fsaverage_forward(epoch)


# #### Generate Inverse

# In[9]:


stc = topomap_3d_brain.create_inverse_solution(epoch, fwd)


# #### Generate figure with pyvista backend (NOT CURRENTLY WORKING)

# In[10]:


#pyvista_brain_fig = topomap_3d_brain.plot_topomap_3d_brain(epoch, stc = stc, backend = 'pyvista')


# #### Save animation with pyvista backend (NOT CURRENTLY WORKING)

# In[11]:


#topomap_3d_brain.save_animated_topomap_3d_brain(pyvista_brain_fig, filename = "brain_animation.gif")


# </br>

# #### Generate figure with matplotlib backend (recommended)

# In[12]:


get_ipython().run_cell_magic('capture', '', "matplot_brain_fig = topomap_3d_brain.plot_topomap_3d_brain(epoch, stc = stc, backend = 'matplotlib')")


# ##### Save the figure

# In[13]:


# You could change the plot to different formats by changing the format argument in the function. 
# It supports 'png', 'pdf', 'svg'.

file_path = "exports/topomap_3d_brain.svg"  # change the file path to where you would like to save the file

matplot_brain_fig.savefig(file_path, format= 'svg')


# #### Generate animation with matplotlib backend (slow but recommended)

# In[ ]:


get_ipython().run_cell_magic('capture', '', "matplotlib_animation = topomap_3d_brain.animate_matplot_brain(epoch, stc = stc, views = 'lat', hemi = 'lh')")


# In[ ]:


matplotlib_animation


# ##### Save the animation as gif

# In[ ]:


get_ipython().run_cell_magic('capture', '', '\nanim_brain = topomap_3d_brain.animate_matplot_brain(epoch, stc = stc, views = \'lat\', hemi = \'lh\')\n\n# use a writer if you want to specify frames per second\nfrom matplotlib.animation import PillowWriter\n\nwriter = PillowWriter(fps=5)\n\ngif_file_path = "exports/topomap_3d_brain.gif"  # change the file path to where you would like to save the file\nanim_brain.save(gif_file_path, writer=writer)')


# #### Save the animation as mp4

# ```{note}
# You would need to save it as gif file first and then convert it into mp4 file.
# ```

# In[ ]:


import moviepy.editor as mp

clip = mp.VideoFileClip("exports/topomap_3d_brain.gif") # change the file path to where you saved the gif file
clip.write_videofile("exports/topomap_3d_brain.mp4")  # change the file path to where you would like to save the file


# <br>
