# Sensing in Biomechanical Processes Lab (SimPL): Extracting and visualizing the human brain state using EEG data 
2021 MDS Capstone Project

# Project Description
Python package and web application for visualizing EEG data

# Helpful Links
- [Proposal Presentation](https://github.com/UBC-MDS/simpl_eeg_capstone/blob/main/reports/Capstone_Proposal_Presentation.pdf)
- [Proposal Report](https://github.com/UBC-MDS/simpl_eeg_capstone/blob/main/reports/Proposal.pdf)
- [Meeting Agendas and Minutes](https://ubc-mds.github.io/simpl_eeg_capstone/)

# Installation Instructions
Clone the repository:
```bash
git clone https://github.com/UBC-MDS/simpl_eeg_capstone.git
cd simpl_eeg_capstone
```

# Package Installation Instructions
Run the following command from the root folder of the project:
```bash
pip install -e .
```

The package contains 6 modules, which can be imported with the following commands:
```python
from simpl_eeg import eeg_objects
from simpl_eeg import raw_voltage
from simpl_eeg import connectivity
from simpl_eeg import topomap_2d
from simpl_eeg import topomap_3d_brain
from simpl_eeg import topomap_3d_head
```

# Running the Web Application
Run the following command from the root folder of the project: 
```bash
streamlit run src/app.py
```

# Group Members
- Matthew Pin
- Mo Garoub
- Yiki Su
- Sasha Babicki

# Mentor
- Joel Ostblom
