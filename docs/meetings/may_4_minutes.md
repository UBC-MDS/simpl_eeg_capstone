
## What we have worked on so far EDA
- Matt walk-through of MNE (topomap)
- Yiki walk-though matplotlib (3D space)
- Lyndia questions: 
	- Can we have non discrete colours for matplotlib - Yiki: yes, should be possible
	- Interpolate rather than discrete points - Matt: should be option for it
- Garoub asking Lyndia for description of what the proposal will be for expected product
- Visualization code package - feed in data, options to choose between visualizations, raw voltage changes, frequency transformation plots, connectivity (correlation between nodes by time), metrics: power changes in each frequency band (moving window in data), 
- Do you have a script that already provides these metrics? Yes, Tim to provide
- UI would be helpful

- Tim - Epochs are slices of data along time (e.g. 1 minute after impact)
- Tim Confirmation - .mat file contains time stamp for impacts
- Evocted data - increase or decrease after stimulis pattern - averaged over timeframe 
	- E.g. P300 potential (positive voltage spike 300ms after stimulis). Hearing tone low tones, and then all of a sudden a high tone, potential change 300ms after. Averaging takes care of the noise over trials. 
- Not known if there would be evocted response after head impact, so far doesn't look like it is there. Still helpful to look at epochs. Continuous visualization is also helpful. 

Metrics and visualizations: 
1) raw voltage values, 
2) power changes, 
3) connectivity
4) 2D head map video, 
5) 3D skull map video, and 
6) 3D brain map with interpolation

Time frame for visualizations - 2 options: 
1) input epoch timing data, select length of time (e.g. list of times interested in 10 seconds before 10 seconds after time point)
2) put in specific start and end time (e.g. 1 to 10 seconds)

Times for current visualization: 
Probably <10 seconds to render, 2 seconds before and after impact

Yiki: Intervals? Sure, average over and have 30 or 60 frames per second

Questions: 

- Each folder is a different experiment: there are 33 head impacts, each different types - lower and higher level etc. 2 minute break between. 

- 2 instances of each? Unsure, Tim to investigate

- File type - import (.set), export (any video format, 2D plots vectorized formats preferrable e.g. .svg)

- Higher number of nodes? Would be nice, but not manditory

- Thoughts on Neurolink? Haven't really looked into it, not implanting devices for now. Not personally comfortable with brain implants. 




