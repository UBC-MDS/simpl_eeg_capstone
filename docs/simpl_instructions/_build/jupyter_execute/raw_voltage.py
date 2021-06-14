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

# ### Define parameters

# A detailed description of all parameters can be found in the `raw_voltage.plot_voltage` docstring:

# In[5]:


help(raw_voltage.plot_voltage)


# In[6]:


# change values below to values of interest

experiment_path = "../../data/927"
nth_epoch = 0


# <br>

# ### Create epoched data

# For additional options see **Creating EEG Objects** section.

# In[7]:


epochs = eeg_objects.Epochs(experiment_path)
epoch = epochs.get_nth_epoch(nth_epoch)


# </br>

# ### Create the raw voltage plot

# #### Generating the plot

# In[8]:


voltage_plot = raw_voltage.plot_voltage(epoch)
voltage_plot;


# #### Saving the plot

# In[9]:


# You can change the plot to different formats by changing the format argument in the function. 
# It supports 'png', 'pdf', 'svg'.

file_path = "../../exports/examples/voltage_plot.svg"  # change the file path to where you would like to save the file

voltage_plot.savefig(file_path, format="svg")


# <br>
