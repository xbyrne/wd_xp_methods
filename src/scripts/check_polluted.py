"""
check_pollution.py
============================
Functionality to check whether a given WD is known to be polluted.
"""

import numpy as np
import pandas as pd

# --------------------------
# Loading external datasets

# GF21xSDSS
gf21sdss = pd.read_csv(
    "../data/external/evaluation/gf21_sdss.csv"
)  # 41820 rows, from VizieR
gf21sdss.drop_duplicates(subset="GaiaEDR3", inplace=True)  # 41820 -> 32169
gf21sdss.set_index("GaiaEDR3", inplace=True)
gf21sdss_index = set(gf21sdss.index)  # Convert to set for faster checking

# MWDD
mwdd = pd.read_csv(
    "../data/external/evaluation/mwdd.csv"
)  # 70698 rows, from MWDD 2024-11-06
mwdd.drop_duplicates(subset="gaiaedr3", inplace=True)  # 70698 -> 61198
mwdd.dropna(inplace=True)  # 61198 -> 56745
mwdd.set_index("gaiaedr3", inplace=True)
mwdd_index = set(mwdd.index)

# PEWDD
pewdd = pd.read_csv(
    "../data/external/evaluation/pewdd.csv"
)  # 3546 rows, from Github 2024-11-06
pewdd.set_index("Gaia_designation", inplace=True)
pewdd = pewdd[pewdd.index.fillna("").str.startswith("Gaia DR3")]  # 3546 -> 2979
pewdd.index = pewdd.index.str.replace("Gaia DR3 ", "")
pewdd_index = set(pewdd.index)


# --------------------------
# Functions to check whether a given WD is known to be polluted
def is_polluted(id_):
    """
    Checks whether a WD with a given Gaia EDR3 ID is polluted.
    Checks GF21xSDSS, PEWDD, and MWDD, and decides based on those.
    Examples:
    - (1, -1, -1) -> 1  (If any of the datasets classify the object as polluted)
    - (0, -1, -1) -> 0  (If a dataset classifies the object as non-polluted)
    - (-1, -1, -1) -> -1  (None of the datasets are conclusive)
    - (1, 0, -1) -> 1  (A dataset saying it's polluted supercedes one saying it's not)
    """
    # If any of the datasets classify the object as polluted, return 1
    # Check them in order so we can return early if a dataset classes the object as polluted
    mwdd_polluted = check_mwdd(id_)
    if mwdd_polluted == 1:
        return 1
    gf21sdss_polluted = check_gf21sdss(id_)
    if gf21sdss_polluted == 1:
        return 1
    pewdd_polluted = check_pewdd(id_)
    if pewdd_polluted == 1:
        return 1

    # If we get to this stage, none of the datasets classify the object as polluted
    checklist = np.array([gf21sdss_polluted, mwdd_polluted, pewdd_polluted])
    # If any of the datasets classify the object as non-polluted, but
    # none of them classify it as polluted, return 0
    if 0 in checklist:
        return 0
    # If none of the datasets are conclusive, return -1
    return -1


def check_gf21sdss(id_):
    """
    Checks whether a WD with a given Gaia EDR3 ID is polluted according to the GF21xSDSS dataset.
    Returns:
    - True: if specClass contains "Z" but doesn't end in "Z:"
    - None: if the object isn't in the dataset, or specClass is "Unreli", "WD", or "UNKN",
            or ends in "Z:"
    - False: otherwise
    """
    if id_ in gf21sdss_index:
        cl = gf21sdss.loc[id_, "specClass"]
        if "Z" in cl and not cl.endswith("Z:"):  # Polluted
            return 1
        if cl in ["Unreli", "WD", "UNKN"] or cl.endswith("Z:"):  # Not sure
            return -1
        # else
        return 0  # Not polluted
    # else
    return -1  # Not sure - not in GF21xSDSS


def check_mwdd(id_):
    """
    Checks whether a WD with a given Gaia EDR3 ID is polluted according to the MWDD dataset.
    Returns:
    - True: if the object is classified as D*Z* in the dataset
    - None: if the object is classified as CND, D, or '?', or isn't in the dataset
    - False: classified as something else
    """
    disqualifying_substrings = ["Z?", "Z:", "+", "/"]
    if float(id_) in mwdd_index:
        cl = mwdd.loc[id_, "spectype"]
        if "Z" in cl:
            if not any(ss in cl for ss in disqualifying_substrings):  # Polluted
                return 1
            if "?" in cl or ":" in cl:  # Not sure, e.g. DZ?, DZ:d
                return -1
        if cl in ["CND", "D", "?"]:  # Not sure
            return -1
        # else
        return 0  # Not polluted
    # else
    return -1  # Not sure - not in MWDD


def check_pewdd(id_):
    """
    Checks whether a WD with a given Gaia EDR3 ID is polluted according to the PEWDD dataset.
    Returns:
    - True: if the object is in the dataset
    - None: otherwise
    """
    if str(id_) in pewdd_index:  # Polluted
        return 1
    # else
    return -1  # Not sure - not in PEWDD
