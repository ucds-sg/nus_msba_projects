

This homework has the following intentions:

1. You should be able to understand how to use HMM for sequential tagging problem.
2. How to adopt the open-sourced code in your own domain? Given the ipython notebook that uses HMM for POS Tagging, you need to modify it for NER. As a data scientist, 80% of your duty should fall into this category. 
3. You should be able to understand the intent of the code and be able to look up google and debug it.


Contents
“Handy” Algorithms
1 Missing Data Imputation
2 Clustering with k-means
3 Clustering Evaluation
4 Other Clustering Algorithms
Homework 2 is due February 19, 2018
“Handy” Algorithms
1 2 3 4 4
Harvard CS 109B, Spring 2018
Jan 23, 2018
In this assignment, you will be working with data collected from a motion capture camera system. The system was used to record 12 different users performing 5 distinct hand postures with markers attached to a left-handed glove. A set of markers on the back of the glove was used to establish a local coordinate system for the hand, and 11 additional markers were attached the the thumb and fingers of the glove. Three markers were attached to the thumb with one above the thumbnail and the other two on the knuckles. Finally, 2 markers were attached to each finger with one above the fingernail and the other in the middle of the finger. A total of 36 features were collected resulting from the camera system. Two other variables in the dataset were the ID of the user and the posture that the user made.
The data were partially preprocessed. First, all markers were transformed to the local coordinate system of the record containing them. Second, each transformed marker with a norm greater than 200 millimeters was eliminated. Finally, any record that contained fewer than three markers was removed.
A few issues with the data are worth noting. Based on the manner in which data were captured, it is likely that, for a given record and user, there exists a near duplicate record originating from the same user. Additionally, There are many instances of missing data in the feature set. These instances are denoted with a ? in the dataset. Finally, there is the potential for imbalanced classes, as there is no guarantee that each user and/or posture is represented with equal frequency in the dataset.
The dataset, provided in CSV format, contains 78,095 rows and 38 columns. Each row corresponds to a single instant or frame as recorded by the camera system. The data are represented in the following manner:

