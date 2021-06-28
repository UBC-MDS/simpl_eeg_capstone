

## Introduction

Electroencephalograms (EEG) is an electrophysiological measurement method used to examine the electrical activity of the brain and represent it as location-based channels of waves and frequencies. Essentially, the EEG data from our dataset is recorded from 19 electrodes nodes for 1.5 hours. Therefore, the EEG data is in high dimensionality and could be represented as a multivariate time series data. If we present the data in a tabular format, the number of rows would be the time stamps and the number of columns would be the different electrodes. As we have 1.5 hrs experiment data and each seconds is recorded at 2048 Hz, which means we have 2048 EEG data readings per second, our dataset is large with at least 1 million rows.

## Objectives

EEG data is widely use in diagnosing brain disorders such as epilepsy and brain damage from head injuries, however, with the complexity of data and its dynamic changes over time, it is hard to identify any significant patterns by simply reading the data or visualizing it. The main objective of this strech goal is to find similar patterns from the combination of EEG signals of all 19 electrodes for a given time section from the dataset. In plain English, it is to cluster the brain states for different time periods in the data. To achieve this, we looked into different clustering methods and created three notebook: 

- Clustering using Kmeans method
- Clustering using Hidden Markov Model
- Other clustering methods 

## Selecting EEG data

We can select the data we want to use with the `simpl_eeg` package. We can either look at individual time steps or time steps averaged over time. We can also specify what time to look at.

For more information about making these selections, please see the page on [Creating EEG Objects](https://ubc-mds.github.io/simpl_eeg_capstone/eeg_objects.html) in the `simpl_eeg` documentation. 

Averaging the data has will reduce the dimensionality of the data, but which method you want to use will depend on what you are trying to achieve. 