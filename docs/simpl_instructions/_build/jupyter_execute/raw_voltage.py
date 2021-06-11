#!/usr/bin/env python
# coding: utf-8

# # Raw Voltage Visualization

# ## Raw voltage plot

# ![](instruction_imgs/voltage_plot.svg)

# In[1]:


from simpl_eeg import raw_voltage, eeg_objects


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


# change values below to values of interest

experiment = "../../data/927" # path to the experiment folder.
nth_epoch = 0


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

# ### Create the raw voltage plot

# #### To generate the plot

# In[7]:


voltage_plot = raw_voltage.plot_voltage(epoch)
voltage_plot;


# #### To save the plot

# In[8]:


# You could change the plot to different formats by changing the format argument in the function. 
# It supports 'png', 'pdf', 'svg'.

file_path = "exports/voltage_plot.svg"  # change the file path to where you would like to save the file

voltage_plot.savefig(file_path, format= 'svg')


# <br>
