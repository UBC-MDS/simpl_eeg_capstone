import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simpl_eeg",
    author="Matthew Pin, Mo Garoub, Yiki Su, Sasha Babicki",
    description="Package for visualizing EEG data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/UBC-MDS/simpl_eeg_capstone",
    project_urls={
        "Bug Tracker": "https://github.com/UBC-MDS/simpl_eeg_capstone/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="simpl_eeg"),
    python_requires=">=3.7",
)