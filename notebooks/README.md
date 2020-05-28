


# Notebooks


This section contains jupyter notebooks that I use in order to process data from deeplabcut.

*Disclaimer* - This is in continuous development depending on my research and is by no means complete. Functions may be added/refactored or removed in future updates.


## Table of Contents
- [notebook 1a - Extract bodypart coordinates during time epochs](#notebook-1a)
- [notebook 1b - Extract Euclidean distance and speed per bodypart](#notebook-1b)
- [notebook 2 - Detection of Freezing and Darting](#notebook-2)
- [notebook 3 - Motion Analysis](#notebook-3)
- [notebook 4 - Validation](#notebook-4)  

### Notebook 1a

**Data Wrangling**

This notebook transforms data from the output of deeplabcut and extracts the x, y coordinates for each body part during specific time epochs. Here they are represented as cs.

**Data Visualization**

There is also the function `plot_bodypart_trajectory()` to plot the location of the animal during specific time epochs.

### Notebook 1b

**Data Transformation**

This notebook transforms data from the output of deeplabcut:
- Extracts euclidean distance between frames for each body part, in specific time epochs
- Calculates the average speed of each bodypart for each particular frame

Saves a file labelled: `file_basename`+`_individual_preprocessing_dlc.csv`

**Data Visualization**  

There is also the function `plot_distance_speed()` to plot the cumulative distance and speed of a bodypart during a specific time epoch.

### Notebook 2

**Data Transformation**  

Extracts freezing/darting events during each time epoch.

*Requires*:   

`_individual_preprocessing_dlc.csv` - from notebook 1b.

*Generates*:   

`file_basename`+`motion_analysis.csv`

**Data Visualization**  

There is also the function `plot_events()` to produce a raster plot of freezing and darting.

### Notebook 3

**Data Transformation**  

Reads data from previous notebooks and calculates for each cs/cs-epoch:    
- freezing(raw, norm),
- darting(raw, norm),
- speed(cm, sec),
- total distance(cm)

*Requires*:    

`_individual_preprocessing_dlc.csv` - from notebook 1b  
`_motion_analysis_dlc.csv` - from notebook 2

*Generates*:  

`file_basename`+`individual_summary_stats.csv`  

** Note **
Contains also a function `concatenate_transformed_dataframes()` that reads a directory and concatenates all the `individual_summary_stats.csv` that are in there.

### Notebook 4

This notebook has some code with the validation of the freezing algorithm.
