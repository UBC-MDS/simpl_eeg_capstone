
# Sensing in Biomechanical Processes Lab (SimPL): Extracting and visualizing the human brain state using EEG data

2021 MDS Capstone Project

# Project Description

Python package and web application for visualizing EEG data. Detailed
instructions on the package, user interface, and clustering stretch goal
can all be found in our [Documentation on GitHub
Pages](https://ubc-mds.github.io/simpl_eeg_capstone/eeg_objects.html).

# Helpful Links

-   [Proposal
    Presentation](https://github.com/UBC-MDS/simpl_eeg_capstone/blob/main/reports/Capstone_Proposal_Presentation.pdf)
-   [Proposal
    Report](https://github.com/UBC-MDS/simpl_eeg_capstone/blob/main/reports/Proposal.pdf)
-   [Final
    Presentation](https://github.com/UBC-MDS/simpl_eeg_capstone/blob/main/reports/Capstone_Final_Presentation.pdf)
-   [Final
    Report](https://github.com/UBC-MDS/simpl_eeg_capstone/blob/main/reports/Final_Report.pdf)
-   [Meeting Agendas and
    Minutes](https://github.com/UBC-MDS/simpl_eeg_capstone/tree/main/docs/minutes/_posts)
-   [Product
    Documentation](https://ubc-mds.github.io/simpl_eeg_capstone/)

# Installation Instructions

Clone the repository:

``` bash
git clone https://github.com/UBC-MDS/simpl_eeg_capstone.git
cd simpl_eeg_capstone
```

If you have no experience working with the unix shell click
[here](https://ubc-mds.github.io/simpl_eeg_capstone/installation.html)
for detailed instructions on installation and launching the Streamlit
app.

# Package Installation Instructions

Full instructions on package installation can be found
[here](https://ubc-mds.github.io/simpl_eeg_capstone/introduction.html)

Run the following command from the root folder of the project:

``` bash
pip install -e .
```

Folders containing EEG data should be moved into the `data` folder in
the root folder of the project.

# Package Usage Instructions

The package contains 6 modules. When using the package directly with
Python you can import each of the modules with the following commands:

``` python
from simpl_eeg import eeg_objects
from simpl_eeg import raw_voltage
from simpl_eeg import connectivity
from simpl_eeg import topomap_2d
from simpl_eeg import topomap_3d_brain
from simpl_eeg import topomap_3d_head
```

# Running the Web Application

As an alternative to using the package directly in Python, you can
access package functionality through a Streamlit web application which
acts as a user interface. To launch the web application, run the
following command from the root folder of the project:

``` bash
streamlit run src/app.py
```

# Updating JupyterBook Documentation

Make sure you have `jupyter-book` and `ghp-import` installed. If you do
not you can install them by running the following commands:

``` bash
pip install -U jupyter-book
pip install ghp-import
```

The files used to generate the documentation are stored in the
[docs/simpl\_instructions/](https://github.com/UBC-MDS/simpl_eeg_capstone/tree/main/docs/simpl_instructions)
folder.

After making updates, run the following commands from the project root
folder to update the online version of the documentation:

``` bash
jb build docs/simpl_instructions/
ghp-import -n -p -f docs/simpl_instructions/_build/html
```

# Group Members

-   Matthew Pin
-   Mo Garoub
-   Yiki Su
-   Sasha Babicki

# Mentor

-   Joel Ostblom

# References

<div id="refs" class="references csl-bib-body hanging-indent">

<div id="ref-jupyterbook" class="csl-entry">

Executable Books Community. 2020. *Jupyter Book* (version v0.10).
Zenodo. <https://doi.org/10.5281/zenodo.4539666>.

</div>

<div id="ref-mne" class="csl-entry">

Gramfort, Alexandre, Martin Luessi, Eric Larson, Denis A. Engemann,
Daniel Strohmeier, Christian Brodbeck, Roman Goj, et al. 2013. “MEG and
EEG Data Analysis with MNE-Python.” *Frontiers in Neuroscience* 7 (267):
1–13. <https://doi.org/10.3389/fnins.2013.00267>.

</div>

<div id="ref-matplotlib" class="csl-entry">

Hunter, J. D. 2007. “Matplotlib: A 2d Graphics Environment.” *Computing
in Science & Engineering* 9 (3): 90–95.
<https://doi.org/10.1109/MCSE.2007.55>.

</div>

<div id="ref-scikit-learn" class="csl-entry">

Pedregosa, F., G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O.
Grisel, M. Blondel, et al. 2011. “Scikit-Learn: Machine Learning in
Python.” *Journal of Machine Learning Research* 12: 2825–30.

</div>

<div id="ref-plotly" class="csl-entry">

Plotly Technologies Inc. 2015. “Collaborative Data Science.” Montreal,
QC: Plotly Technologies Inc. 2015. <https://plot.ly>.

</div>

</div>
