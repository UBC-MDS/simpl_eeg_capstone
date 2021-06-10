#!/usr/bin/env python
# coding: utf-8

# # Creating EEG Objects

# ## Epoch Creation

# In[1]:


from simpl_eeg import eeg_objects


# In[2]:


import warnings
warnings.filterwarnings('ignore')


# **Please include the line below in your IDE so that the changes would be simultaneously reflected when you make a change to the python scripts.**

# In[3]:


get_ipython().run_line_magic('load_ext', 'autoreload')


# In[4]:


get_ipython().run_line_magic('autoreload', '2')


# <br>

# ### Module Overview

# The `eeg_objects` module contains helper classes for storing and manipulating relevant information regarding epochs to pass to other package functions. It contains two classes. Typically you will only you use the `eeg_objects.Epochs` directly, which by default contains a `eeg_objects.EEG_File` object in the `eeg_file` attribute. 
# Below are the docstrings for the two classes:

# In[5]:


# Class for reading and importing EEG files
get_ipython().run_line_magic('pinfo', 'eeg_objects.EEG_File')


# In[6]:


# Class for storing, generating, and adjusting epoch objects
get_ipython().run_line_magic('pinfo', 'eeg_objects.Epochs')


# <br>

# ### Define parameters

# The only required parameter to create an epoch object is the `folder_path` for the experiment of interest, however additional parameters may be used to customize your epoch object. 
# 
# If you specify a `start_second`, a single epoch will be generated with an impact event at the specified second. 
# 
# If you do not specify a `start_second`, epochs will be automatically generated using the impact times found in the `impact locations.mat` file in the selected `experiment_folder`. 
# 
# `tmin` specifies the number of seconds before the impact to use, and `tmin` specifies the number of seconds after the impact.

# In[7]:


experiment_folder = "../../data/109" # path to the experiment folder
tmin = -1  # number of seconds before the impact, should be a negative number for before impact
tmax = 1  # number of seconds after the impact
start_second = None  # if creating a custom epoch, select a starting second


# <br>

# ### Create epoched data

# You can create epoched data using the `Epochs` class.

# In[8]:


epochs = eeg_objects.Epochs(experiment_folder, tmin, tmax, start_second)


# The generated epoch data is found within the `data` attribute. Here we are generating epochs with automatically detected impact times, so we can see that there are multiple events.

# In[9]:


epochs.data


# If instead we create epochs with a custom start second, we will only create a single epoch with an impact the given `start_second`.

# In[10]:


start_second = 15  # record event at second 15
custom_epoch = eeg_objects.Epochs(experiment_folder, tmin, tmax, start_second) 

custom_epoch.data


# #### Get information about epochs

# In addition to the epochs contained in the `data` attribute, the `Epoch` object also contains information about the file used and has a selected epoch for quick access. 

# In[11]:


eeg_file = epochs.eeg_file
print(eeg_file.folder_path)  # experiment folder path
print(eeg_file.experiment)  # experiment number
print(eeg_file.mat)  # impact times
print(eeg_file.raw)  # raw data


# #### Select specific epoch

# If you have a specific epoch of interest you can specify it with the `set_nth_epoch` method. Then to retrieve that epoch use `get_nth_epoch`

# In[12]:


nth_epoch = 5  # the epoch of interest to select, the 6th impact
epochs.set_nth_epoch(nth_epoch)


# In[13]:


single_epoch = epochs.get_nth_epoch()
single_epoch


# #### Decimate the epoch (optional)

# To reduce the size of the selected epoch you can choose to skip a selected number of time steps by calling the `skip_n_steps` method. This will only be run on the current selected epoch from the previous step, contained in the `epoch` attribute.
# 
# Skipping steps will greatly reduce animation times for the other functions in the package. The greater the number of steps skipped, the fewer the frames to animate. In the example below we are reducing the selected epoch from 4097 time steps to 81 time steps. 

# In[14]:


single_epoch.get_data().shape


# In[15]:


num_steps = 50
smaller_epoch = epochs.skip_n_steps(num_steps)
smaller_epoch.get_data().shape


# ### MNE functions

# Now that you have access epoched data, you can use the `simpl_eeg` package functions as well as any [MNE functions](https://mne.tools/stable/generated/mne.Epochs.html) which act on `mne.epoch` objects. Below are some useful examples for the MNE objects contained within the object we created. 

# #### Raw data
# https://mne.tools/stable/generated/mne.io.Raw.html

# In[16]:


raw = epochs.eeg_file.raw
raw.info


# In[17]:


raw.plot_psd();


# #### Epoch data

# In[18]:


# first 3 epochs
epochs.data.plot(n_epochs=3);


# In[19]:


# specific epoch
epochs.get_nth_epoch().plot();  # alternatively you could call epochs.epoch directly


# In[20]:


# specific epoch with steps skipped
epochs.skip_n_steps(100).plot();

