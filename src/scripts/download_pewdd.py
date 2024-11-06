"""
download_pewdd.py
=================
Downloads the Planetary Enriched White Dwarf Database (Williams+24).
This is downloaded as an extra source of pollution labels for the XP spectra.
"""

import pandas as pd

PEWDD_URL = "https://raw.githubusercontent.com/jamietwilliams/PEWDD/main/PEWDD.csv"
pewdd = pd.read_csv(PEWDD_URL)

pewdd.to_csv("../data/external/pewdd.csv")
