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


# change None to values of interest

experiment = None # has to be a string
nth_epoch = None


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

# ### Create the raw voltage plot

# #### To generate the plot

# In[ ]:


voltage_plot = raw_voltage.plot_voltage(epoch)
voltage_plot;


# #### To save the plot

# In[ ]:


# You could change the plot to different formats by changing the format argument in the function. 
# It supports 'png', 'pdf', 'svg'.

voltage_plot.savefig("voltage_plot.svg", format= 'svg')


# <br>

# In[ ]:




