# Sensing in Biomechanical Processes Lab (SimPL): Extracting and visualizing the human brain state using EEG data 
2021 MDS Capstone Project

# Project Description
Python package and web application for visualizing EEG data

# Helpful Links
- [Proposal Presentation](https://github.com/UBC-MDS/simpl_eeg_capstone/blob/main/reports/Capstone_Proposal_Presentation.pdf)
- [Proposal Report](https://github.com/UBC-MDS/simpl_eeg_capstone/blob/main/reports/Proposal.pdf)
- [Final Presentation](https://github.com/UBC-MDS/simpl_eeg_capstone/blob/main/reports/Capstone_Final_Presentation.pdf)
- [Final Report](https://github.com/UBC-MDS/simpl_eeg_capstone/blob/main/reports/Final_Report.pdf)
- [Meeting Agendas and Minutes](https://github.com/UBC-MDS/simpl_eeg_capstone/tree/main/docs/minutes/_posts)
- [Product Documentation](https://ubc-mds.github.io/simpl_eeg_capstone/)

# Installation Instructions
Clone the repository:
```bash
git clone https://github.com/UBC-MDS/simpl_eeg_capstone.git
cd simpl_eeg_capstone
```
If you have no experience working with the unix shell click [here](https://ubc-mds.github.io/simpl_eeg_capstone/installation.html) for detailed instructions on installation and launching the Streamlit app.

# Package Installation Instructions
Run the following command from the root folder of the project:
```bash
pip install -e .
```

# Package Usage Instructions
The package contains 6 modules. When using the package directly with Python you can import each of the modules with the following commands:
```python
from simpl_eeg import eeg_objects
from simpl_eeg import raw_voltage
from simpl_eeg import connectivity
from simpl_eeg import topomap_2d
from simpl_eeg import topomap_3d_brain
from simpl_eeg import topomap_3d_head
```

# Running the Web Application
As an alternative to using the package directly in Python, you can access package functionality through a Streamlit web application which acts as a user interface. To launch the web application, run the following command from the root folder of the project: 
```bash
streamlit run src/app.py
```

# Updating JupyterBook Documentation
Make sure you have `jupyter-book` and `ghp-import` installed. If you do not you can install them by running the following commands: 
```bash
pip install -U jupyter-book
pip install ghp-import
```

The files used to generate the documentation are stored in the [docs/simpl_instructions/](https://github.com/UBC-MDS/simpl_eeg_capstone/tree/main/docs/simpl_instructions) folder. 

After making updates, run the following commands from the project root folder to update the online version of the documentation:

```bash
jb build docs/simpl_instructions/
ghp-import -n -p -f docs/simpl_instructions/_build/html
```

# Group Members
- Matthew Pin
- Mo Garoub
- Yiki Su
- Sasha Babicki

# Mentor
- Joel Ostblom
