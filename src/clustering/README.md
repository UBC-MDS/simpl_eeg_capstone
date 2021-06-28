

## Introduction

Electroencephalogram (EEG) is an electrophysiological measurement method used to examine the electrical activity of the brain and represent it as location-based channels of waves and frequencies. The EEG data from our dataset was recorded from 19 electrodes for the period of one and half hours. The data is in high dimensionality and could be represented as a multivariate time series data. If we present the data in a tabular format, the number of rows would be the time stamps and the number of columns would be the different electrodes. Each experiment had 1.5 hours of data and each second was recorded at 2048 HZ, which means that we had 2048 EEG data readings per second. Hence, our dataset was quite large with at least one million rows.

## Objectives

EEG data is widely used in diagnosing brain disorders such as epilepsy and brain damage from head injuries; however, with the complexity of the brain data and its dynamic changes over time, it is hard to identify significant patterns by simply reading the data or visualizing it. Our main objective is to find similar patterns from the combination of EEG signals of all 19 electrodes for a given time section from the dataset. Simply, the objective is to cluster the brain states for different time periods in the data. To achieve this, we looked into different clustering methods and created three notebook: 

- Clustering using Kmeans method
- Clustering using Hidden Markov Model
- Other clustering methods 

## Selecting EEG data

We can select the data we want to use with the `simpl_eeg` package. We can either look at individual timestamps or time steps averaged over time. We can also specify what time to look at.

For more information about making these selections, please see the page on [Creating EEG Objects](https://ubc-mds.github.io/simpl_eeg_capstone/eeg_objects.html) in the `simpl_eeg` documentation. 

Averaging the data will reduce the dimensionality of the data; however, the method you want to use will depend on what you are trying to achieve. 