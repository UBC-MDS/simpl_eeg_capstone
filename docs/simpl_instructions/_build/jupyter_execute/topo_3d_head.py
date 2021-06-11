#!/usr/bin/env python
# coding: utf-8

# # 3D Head Visualizations

# ##  Topographic map in 3D head

# ![](instruction_imgs/topo_3d_head_ani.gif)

# In[1]:


from simpl_eeg import eeg_objects, topomap_3d_head


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

# ### Define global parameters

# There are some common parameters for all functions in this package, it would be more convenient to define all parameters before going into each functions.

# In[5]:


# change values below to values of interest

experiment = "../../data/927"  # path to the experiment folder.
nth_epoch = 0
color_min = -40  # the minimum voltage to show on the colorbar
color_max = 40  # the minimum voltage to show on the colorbar
colormap = "RdBu_r"  # select from ["RdBu_r", "hot", "cool", "inferno", "turbo", "rainbow"]


# <br>

# ### Create epoched data

# In[6]:


tmin = -0.3  # number of seconds before the impact. Please change it to a value of your interest
tmax = 0.7  # number of seconds after the impact. Please change it to a value of your interest
start_second = None  # starting time of the epoch. Please change it to a value of your interest

raw = eeg_objects.Epochs(experiment, tmin, tmax, start_second)

raw.set_nth_epoch(nth_epoch)

epoch = raw.get_nth_epoch()


# </br>

# ### Create the topographic map in 3D head shape

# In[7]:


timestamp = -300  # you can change the value to the time stamp of your interest
topo_3d__head_static = topomap_3d_head.topo_3d_map(
    epoch,
    time_stamp,
    color_title="EEG MicroVolt",
    color_min=color_min,
    color_max=color_max,
    colormap=colormap,
)


# In[ ]:


topo_3d__head_static.show()


# #### Generating the animnation

# In[ ]:


topo_3d_head = topomap_3d_head.animate_3d_head(
    epoch,
    color_title="EEG MicroVolt",
    color_min=color_min,
    color_max=color_max,
    colormap=colormap,
)


# In[ ]:


topo_3d_head.show()


# #### Saving the animnation

# ##### Save the static plot

# In[ ]:


static_file_path = "exports/topo_3d_static.svg"  # change the file path to where you would like to save the file

topo_3d__head_static.write_image(static_file_path, engine="kaleido")


# In[ ]:


static_file_path_png = "exports/topo_3d_static.png"  # change the file path to where you would like to save the file

topo_3d__head_static.write_image(static_file_path_png) # no need to specify engine if not saved as svg file


# ##### Save the animation as html

# In[ ]:


html_file_path = "exports/topo_3d.html"  # change the file path to where you would like to save the file

topo_3d_head.write_html(html_file_path)


# ##### Save the animation as gif

# In[ ]:


topomap_3d_head.save_gif(epoch, gifname="topo_3d_head_ani", duration=200) 


# ##### Save the animation as mp4 

# ```{note}
# You would need to save it as gif file first and then convert it into mp4 file.
# ```

# In[ ]:


import moviepy.editor as mp

clip = mp.VideoFileClip("topo_3d_head_ani.gif")  # change the file path to where you saved the gif file
clip.write_videofile("topo_3d_head_ani.mp4")  # change the file path to where you would like to save the file


# In[ ]:




