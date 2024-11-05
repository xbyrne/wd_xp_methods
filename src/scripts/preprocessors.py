"""
preprocessors.py
================
Functions for preprocessing the raw Gaia XP data.
"""

import numpy as np
import pandas as pd


def divide_Gflux(xp_coeffs, ids):
    """
    Normalises the coefficients by the flux in the G band, found from GF+21
    """
    gf21 = pd.read_csv("../data/external/gf21.csv")
    gf21.set_index("GaiaEDR3", inplace=True)

    Gmag = gf21.loc[ids, "Gmag"].values
    Gflux = 10 ** (-0.4 * (Gmag - 25.7934))
    # This offset is arbitrary  ^^^^^^^^^
    # It's the Gaia G zeropoint for AB mags, and ensures
    # coefficient values are not too big/small: log(coeff) ~ -4 +/- 1
    # Doesn't affect relative proximities of points,
    # just makes numerics more stable

    return xp_coeffs / Gflux[:, None]


def l2_norm(xp_coeffs):
    """
    Normalises the coefficients by the L2 norm
    """
    return xp_coeffs / np.linalg.norm(xp_coeffs, axis=1)[:, None]
