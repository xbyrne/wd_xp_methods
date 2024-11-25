"""
check_known_polluted.py
=======================
Checks PEWDD, MWDD, and GF21xSDSS for whether a WD is polluted.
Stores a csv file with two columns:
- Gaia EDR3 ID
- isPolluted:
    - 1 if the object has been classified as polluted in any of the datasets
    - 0 if none of the datasets classify the object as polluted, unless any *do*
    - -1 if it is possible that the object is polluted, but not confirmed
Inspect `check_{dataset}` functions for more details on how the classification is done.
"""

import numpy as np
import pandas as pd
from tqdm import tqdm

fl = np.load("../data/interim/xp_coeffs.npz")
ids = fl["ids"]  # 107164 Gaia EDR3 IDs

# --------------------------
# Loading external datasets, and selecting the objects which have XP spectra (`ids`)
# GF21xSDSS
gf21sdss = pd.read_csv("../data/external/gf21_sdss.csv")  # 41820 rows, from VizieR
gf21sdss.drop_duplicates(subset="GaiaEDR3", inplace=True)  # 41820 -> 32169
gf21sdss.set_index("GaiaEDR3", inplace=True)
gf21sdss = gf21sdss.loc[
    list(set(gf21sdss.index).intersection(set(ids)))  # In both GF21xSDSS and XP sample
]  # 32169 -> 10936

# MWDD
mwdd = pd.read_csv("../data/external/mwdd.csv")  # 70698 rows, from MWDD 2024-11-06
mwdd.drop_duplicates(subset="gaiaedr3", inplace=True)  # 70698 -> 61198
mwdd.dropna(inplace=True)  # 61198 -> 56745
mwdd.set_index("gaiaedr3", inplace=True)
mwdd = mwdd.loc[
    list(set(mwdd.index).intersection(set(ids)))  # In both MWDD and XP sample
]  # 56745 -> 11939

# PEWDD
pewdd = pd.read_csv("../data/external/pewdd.csv")  # 3546 rows, from Github 2024-11-06
pewdd.set_index("Gaia_designation", inplace=True)
pewdd = pewdd[pewdd.index.fillna("").str.startswith("Gaia DR3")]  # 3546 -> 2979
pewdd.index = pewdd.index.str.replace("Gaia DR3 ", "").astype(int)

# --------------------------
# Instantiating the output dataframe
ispolluted = pd.DataFrame(index=ids, columns=["is_polluted"])
# is_polluted can be True, False, or None


# --------------------------
# Functions to check whether a given WD is known to be polluted
def check_whether_obj_polluted(id_):
    """
    Checks whether a WD with a given Gaia EDR3 ID is polluted.
    Checks GF21xSDSS, PEWDD, and MWDD, and decides based on those.
    Examples:
    - (1, -1, -1) -> 1  (If any of the datasets classify the object as polluted)
    - (0, -1, -1) -> 0  (If a dataset classifies the object as non-polluted)
    - (-1, -1, -1) -> -1  (None of the datasets are conclusive)
    - (1, 0, -1) -> 1  (A dataset saying it's polluted supercedes one saying it's not)
    """
    gf21sdss_polluted = check_gf21sdss(id_)
    mwdd_polluted = check_mwdd(id_)
    pewdd_polluted = check_pewdd(id_)
    checklist = np.array([gf21sdss_polluted, mwdd_polluted, pewdd_polluted])

    # If any of the datasets classify the object as polluted, return 1
    if 1 in checklist:
        return 1
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
    if id_ in gf21sdss.index:
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
    - None: if the object isn't in the dataset
    - False: otherwise
    """
    disqualifying_substrings = ["Z?", "Z:", "+", "/"]
    if id_ in mwdd.index:
        cl = mwdd.loc[id_, "spectype"]
        if "Z" in cl and not any(
            ss in cl for ss in disqualifying_substrings
        ):  # Polluted
            return 1
        if cl == "CND":  # Not sure
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
    if id_ in pewdd.index:  # Polluted
        return 1
    # else
    return -1  # Not sure - not in PEWDD


if __name__ == "__main__":
    for idd in tqdm(ids):
        isp = check_whether_obj_polluted(idd)
        ispolluted.loc[idd, "is_polluted"] = isp

    ispolluted.to_csv("../data/interim/is_polluted.csv", index_label="gaiaedr3")
