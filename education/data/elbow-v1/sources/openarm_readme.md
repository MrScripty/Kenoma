This readme.md file was generated on 2021-07-08 by Laura A. Hallock.

---

# GENERAL INFORMATION

This folder contains the OpenArm Multisensor 2.0 data set, a set of multi-subject time series sensor data collected from the elbow flexors during varied isometric contraction and trajectory tracking tasks. Data include cross-sectional ultrasound images of the brachioradialis (both raw and processed to extract time-varying muscle thickness), as well as time series trajectories of ultrasound-measured thickness of the brachioradialis, sEMG-measured activation of the biceps, and net output force at the elbow. While this data is provided primarily for exploration and validation of the publication listed below, we invite anyone in the research community to use it in their own modeling endeavors.

This data set comprises data from 10 subjects. Full details of the data collection process can be found in the publication below.

Data are best examined using the open-source code available [here](https://github.com/lhallock/openarm-multisensor). Note that the subjects examined here and their identifying numbers bear no relation to those examined in previous OpenArm releases, including OpenArm Multisensor 1.0.

Questions about the data set should be directed to:

	Laura A. Hallock
	PhD Student, UC Berkeley EECS
	lhallock@eecs.berkeley.edu

Data were collected at UC Berkeley, Berkeley, California, 2021-05. The collection process was approved by the University of California Institutional Review Board for human protection and privacy, under Protocol ID 2016-01-8261.

Data collection and analysis were supported by the NSF National Robotics Initiative (award no. 81774), Siemens Healthcare (85993), the NVIDIA Corporation GPU Grant Program, eZono AG, and the NSF Graduate Research Fellowship Program.

---

# SHARING/ACCESS INFORMATION

This work is licensed under a Creative Commons Attribution 4.0 International License: https://creativecommons.org/licenses/by/4.0/

If you use these data for academic research, please cite the following publication:

Laura A. Hallock, Bhavna Sud, Chris Mitchell, Eric Hu, Fayyaz Ahamed, Akash Velu, Amanda Schwartz, and Ruzena Bajcsy, "Toward Real-Time Muscle Force Inference and Device Control via Optical-Flow-Tracked Muscle Deformation," in IEEE Transactions on Neural Systems and Rehabilitation Engineering (TNSRE), IEEE, 2021. (under review)

---

# DATA & FILE OVERVIEW

This archive contains time series sensor data from the arms of 10 subjects (denoted Sub1-Sub10 in both this file release and the accompanying publication). Based on file size and for ease of download, data are organized in three folders as follows:

`ultrasound_frames` - Time series frames (both raw and processed to extract muscle thickness) of ultrasound data, alongside text files listing this time series extracted thickness at each frame, collected at approximately 100 Hz. (Note that these text files *almost* replicate the thickness time series below, but are collected at the same rate and aligned with the saved image frames.) Frames are JPEG images, and data are released in per-subject ZIP archives for ease of download.

`time_series` - Time series data streams (both raw and filtered as described in the publication above, collected at approximately 1 KHz), including ultrasound-measured thickness of the brachioradialis, sEMG-measured activation of the biceps, and net output force at the elbow, as well as a displayed target trajectory, along with measures of each subject's maximal and minimal force output for each trial. Data are stored in Python pickle archive files and are best accessed via the linked code above. Data are released in a single ZIP archive for ease of code interfacing.

`demographics_&_survey` - Subject demographics and responses to survey on deformation- and activation-based trajectory tracking controller preferences, including CSV and PDF demographic information, a PDF of the presented survey, and both CSV and PDF versions of aggregated subject responses.

A comprehensive explanation of how these data can be accessed and manipulated can be found in the codebase linked above and its associated README.

---

# FILE LIST

```bash
.
├── time_series.zip # all time series data streams
│   ├── [N] # all time series data for Sub[N], including thickness, activation, force, and target trajectory, raw and processed, with maximum and minimum values
│   │   ├── trial_0.p # data for test trial (all streams displayed, no instructed task)
│   │   ├── trial_1a.p # data for first correlation trial (force displayed, instructed to track)
│   │   ├── trial_1b.p # data for second correlation trial (force displayed, instructed to track)
│   │   ├── trial_2a.p # data for first deformation (ultrasound) tracking trial (thickness/deformation displayed, instructed to track)
│   │   ├── trial_2b.p # data for second deformation (ultrasound) tracking trial (thickness/deformation displayed, instructed to track)
│   │   ├── trial_3a.p # data for first activation (sEMG) tracking trial (activation displayed, instructed to track)
│   │   └── trial_3b.p # data for second activation (sEMG) tracking trial (activation displayed, instructed to track)
│   ├── ...
├── ultrasound_frames # all ultrasound frames, both raw and processed (filtered and with tracked points) to extract muscle thickness
│   ├── [N].zip # all frames for Sub[N]
│   │   ├── images_[t]_filtered # ultrasound time series data for Sub[N] trial [t], processed (filtered and with tracked points)
│   │   │   ├── [k].jpg # filtered frame at system time [k]
│   │   │   ├── ...
│   │   ├── images_[t]_raw # ultrasound time series data for Sub[N] trial [t], raw
│   │   │   ├── [k].jpg # raw frame at system time [k]
│   │   │   ├── ...
│   │   ├── trial_[t].txt # corresponding list of extracted brachioradialis thicknesses at each frame for trial [t]
│   │   ├── ...
│   ├── ...
├── demographics_&_survey # demographic and survey information
│   ├── demographics.csv # primary demographic information by subject
│   ├── demographics.pdf # all demographic information by subject (incl. additional information on exercise and computer interface familiarity)
│   ├── tracking_survey.pdf # copy of the post-experiment tracking survey administered to subjects
│   ├── tracking_survey_responses.pdf # survey responses by subject (incl. free form answers)
│   ├── survey_us.csv # survey responses to deformation-based (ultrasound) tracking (used in analysis)
│   ├── survey_emg.csv # survey responses to activation-based (sEMG) tracking (used in analysis)
│   └── survey_comp.csv # survey responses comparing deformation- and activation-based tracking (used in analysis)
├── errata.md # list of deviations from expected filetree outlined in this document
└── readme.md # this document
```
