# HPLC chromatogramm scripts

Python 3 scripts to handle and convert EZCHROM ASCII-files.

# fhplc.py

Read .asc files and convert them to easily importable .txt files. Plot the chromatogramms with Matplotlib for a quick visualization.

# fhplc_fit_gauss.py

Fit multiple Gaussian curves to .asc files and report AUC for peak 2. Fits are visualized with Matplotlib. AUC values of all input files are written to a .txt file.

# TO DO
- change fhplc_fit_gauss.py to identify the peaks for fitting automatically
- implement a way to automatically handle the amount of curves that are processed per file
- use input path for .asc files
- allow out path and custom dir names
