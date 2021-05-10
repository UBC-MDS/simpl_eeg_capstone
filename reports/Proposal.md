# DSCI 591: Capstone Project – Proposal Report for Sensing in Biomechanical Processes Lab (SimPL)

**Team members**: Matthew Pin, Mo Garoub, Sasha Babicki, Zhanyi (Yiki) Su

**Project mentor**: Joel Ostblom

**Date**: May 13, 2021

## 3.1. Executive Summary
**<A brief and high level summary of the project proposal>**
  
## 3.2 Introduction
### 3.2.1 Overview
SimPL is a research lab in the department of Mechanical Engineering at UBC. They are developing quantitative and sensitive methods to evaluate the electrophysiological changes after sport head injuries. In addition, SimPL is developing mobile brain and body imaging system, head impact detection using machine learning, and investigating concussion mechanisms.

Concussion and brain injuries in general are invisible. The underlying mechanisms of brain dysfunction is not clear yet. SimpPL have employed electroencephalograms (EEG) to measure and detect potential changes in the brain electrophysiology due to sports head impacts. The team was approached to design novel solutions and methods to extract and visualize the human brain state using EEG data and data science techniques learned in the MDS program. We have received a set of EEG data containing multi-participant and multi-trial experimental data with multichannel EEG information.

**<WHAT IS THE QUESTION WE ARE ANSWERING/PROBLEM WE ARE SOLVING AND WHY IS IT IMPORTANT?>**

After gathering data and having multiple meetings with the partner and mentor, we decided as a team to propose to deliver the following products:
1) A Python package containing EEG visualization and metric functions
2) An interactive web app to provide a user interface for the package

In addition to our main deliverables, we have the following stretch goals which will be produced if time permits:
1) Additional functionality for the Python package for EEG preprocessing steps
2) Answering a research question by building a data pipeline for unsupervised learning methods such as clustering

### 3.2.1 Main Goals
We will be designing a custom Python package which will conveniently provide the ability to produce advanced visualizations and metrics for EEG data. The package will be well documented and will allow for future customization by the lab members at SimPL. The package at a minimum include the following functionality:
1) Raw voltage values
2) Power changes
3) Connectivity
4) 2D head map video
5) 3D skull map video
6) 3D brain map with interpolation

In addition to the package, we will build an Interactive UI (user interface) using a Streamlit web application. The web application will be accessible by running a simple command and will contain the functionality provided by the package. Additionally, there will be widgets for customization of settings for the functions. At a minimum, the widgets will provide the following options: 
1) File upload
    - Depending on the preferences of the partner, this can be linked directly to their local files of files on cloud
    - If requested by the partner, a file upload option would also be possible to implement
2) Two time selection options
    - The user may input epoch timing data and then select epochs to display
    - The user may input a specific start time and duration of the animation
3) Frame rate
    - The frame rate for the animations

### 3.2.2 Stretch goals
Stretch goals will be delivered only if enough time is available after completing the main deliverables. Stretch goals will be selected based on discussion with the Capstone partner and mentor.

The first possible stretch goal is to add additional package functionality for preprocessing steps. We would implement the ability to preprocess uncleaned EEG data using the package created in our main goal.

The second possible stretch goal is to create a data pipeline for clustering, which is an unsupervised learning method. The goal of the pipeline is to identify potential patterns in EEG data. It might involve decomposing the signal into alpha, beta, theta, and delta waves to look for structure, and then use a Markov model or hidden Markov model to carry out the clustering task. 

## 3.3. Data Science Techniques
### 3.3.1 Source Data
We will be using cleaned EEG data from the 8 provided experiments as input for our main goals. Each experiment is expected to have: 
- `fixica.set` (metadata) 
- `fixica.fdt` (raw data)
- `impact locations.mat` (times of impact)
- `____.mat` (?????)
- 33 impacts per experiment
- 9 channels, one for each electrode
- Approximate duration of 1.5 hours
- Sampling rate of 2048 Hz

### 3.3.2 Techniques
For the package containing functions for EEG visualization and metrics we will be using Python. Most of the functions will make use of an existing open source library called [MNE](https://mne.tools/stable/index.html). In addition to MNE we expect to use the [Matplotlib](https://matplotlib.org/) library for certain visualizations. The package will only contain functions which the partner finds useful and will be customized for their purposes, so it should be more convenient than using MNE or Matplotlib directly. It will be well documented and easy for the partner to update as needed after the Capstone project is complete. 
- Data for each experiment is relatively large (1GB) due to high dimensionality (19 nodes * 1.5 hours sampled at 2048 Hz), leading visualizations to take a long time to render
- Many MNE functions require evoked data, so wrangling will need to be done in order to convert the data into a format that can be processed

For the interactive user interface we are planning to use [Streamlit](https://streamlit.io/), which is an open source Python framework for turning Python scripts into web apps. The benefit of Streamlit is that it is very lightweight and does not require any front-end experience. The framework is very intuitive, so users who understand Python should be able to update the code as needed with minimal understanding of Streamlit. 
- There are many visualizations to show, so designing an informative and easy to use UI will be a challenge

For the preprocessing function extension of our python package we will use the MNE library.
- Cleaning EEG data is a difficult process as there is a lot of noise in EEG data
- Currently the Capstone partner is using EEGLAB for cleaning their EEG data, which is software with a GUI which is specifically designed for processing EEG data. - - Adding pre-processing functionality may be helpful for keeping everything in one place, but it would be difficult to compete with the functionality of EEGLAB. 

For the machine learning classification/clustering, we will likely use [SciPy](https://www.scipy.org/) to perform the data wrangling to decompose data into different frequency bandwidth. The Capstone partner has suggested we use the Markov model or the Hidden Markov model for the clustering tasks. Other researchers have historically used k-means clustering, support vector machine (SVM) or CNN models to do the classification, which we may also try. We would use [scikit-learn](https://scikit-learn.org/stable/) or [PyTorch](https://pytorch.org/) to build the pipeline. The pipeline can be delivered in either a Jupyter notebook or Python script, based on the Capstone partner’s preferences. 
- Domain expertise required for interpretation, so identifying clusters may be difficult without a lot of assistance from the capstone partner
- Data likely does not contain significant results based on what the partner has told us, so searching for patterns may be fruitless


## 3.4 Timeline
**Milestone 1 - May 17, 2021**
MVP for Python package visualizations and metrics (6 functions)

**Milestone 2 - May 26, 2021**
MVP for interactive user interface, first round improvements for package

**Milestone 3 - June 7, 2021**
MVP for preprocessing addition to package and ML classification, first round improvements for UI

**Milestone 4 - June 22, 2021**
Report and touch-ups for previous milestones
