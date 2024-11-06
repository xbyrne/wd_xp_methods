"""
check_known_polluted.py
=======================
Checks PEWDD, MWDD, and GF21xSDSS for whether a WD is polluted.
Stores a csv file with two columns:
- Gaia EDR3 ID
- isPolluted:
    - `True` if the object has been classified as polluted in any of the datasets
    - `False` if none of the datasets classify the object as polluted, unless any *do*
    - `None` if it is possible that the object is polluted, but not confirmed
Inspect `check_{dataset}` functions for more details on how the classification is done.
"""

import numpy as np
import pandas as pd
from tqdm import tqdm

fl = np.load("../data/interim/xp_coeffs.npz")
ids = fl["ids"]  # 107164 Gaia EDR3 IDs


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
pewdd = pewdd[pewdd.index.str.startswith("Gaia DR3") == True]  # 3546 -> 2979
pewdd.index = pewdd.index.str.replace("Gaia DR3 ", "").astype(int)


# Instantiating the output dataframe
ispolluted = pd.DataFrame(index=ids, columns=["isPolluted"])
# isPolluted can be True, False, or None


def check_whether_obj_polluted(id_):
    """
    Checks whether a WD with a given Gaia EDR3 ID is polluted.
    Checks GF21xSDSS, PEWDD, and MWDD, and decides based on those.
    Examples:
    - (True, None, None) -> True
    - (False, None, None) -> False
    - (None, None, None) -> None
    - (True, None, False) -> True
    """
    gf21sdss_polluted = check_gf21sdss(id_)
    mwdd_polluted = check_mwdd(id_)
    pewdd_polluted = check_pewdd(id_)

    if any([gf21sdss_polluted, mwdd_polluted, pewdd_polluted]):
        # (True, True, True), (True, True, None), (True, True, False),
        # (True, None, None), (True, None, False), (True, False, False) + cyc.
        return True
    if all([gf21sdss_polluted is None, mwdd_polluted is None, pewdd_polluted is None]):
        # (None, None, None)
        return None
    # else
    # (None, None, False), (None, False, False), (False, False, False) + cyc.
    return False


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
        if "Z" in cl and not cl.endswith("Z:"):
            return True
        if cl in ["Unreli", "WD", "UNKN"] or cl.endswith("Z:"):
            return None
        # else
        return False
    # else
    return None


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
        if "Z" in cl and not any(ss in cl for ss in disqualifying_substrings):
            return True
        if cl == "CND":
            return None
        # else
        return False
    # else
    return None


def check_pewdd(id_):
    """
    Checks whether a WD with a given Gaia EDR3 ID is polluted according to the PEWDD dataset.
    Returns:
    - True: if the object is in the dataset
    - None: otherwise
    """
    if id_ in pewdd.index:
        return True
    # else
    return None


if __name__ == "__main__":
    for idd in tqdm(ids):
        isp = check_whether_obj_polluted(idd)
        ispolluted.loc[idd, "isPolluted"] = isp

    ispolluted.to_csv("../data/interim/is_polluted.csv")
