"""
process_xp.py
=============
This script processes the raw Gaia XP data, creating the file
`data/interim/xp_coeffs.npz`. This file contains:
- `ids` -- the Gaia EDR3 IDs
- `xp` -- the XP coefficients
- `xp_err` -- the errors on the XP coefficients
"""

from ast import literal_eval
import numpy as np
import pandas as pd
from gaiaxpy import calibrate


def read_xp_to_arrays(filename):
    """
    Converts a .csv file containing XP coefficients (and errors) to numpy arrays
    Doesn't return the correlations between the coefficients (yet..?)
    Returns:
    - gaia_ids: The Gaia EDR3 IDs (N,)
    - xp_coeffs: The XP coefficients (N, 110)
    - xp_errs: The errors on the XP coefficients (N, 110)
    """

    print("Reading table...")
    xp_spectra_table = pd.read_csv(filename)  # ~1min

    print("Extracting data...")
    gaia_ids = np.array(xp_spectra_table["source_id"])

    bp_coeffs = np.array(
        [literal_eval(coeffs) for coeffs in xp_spectra_table["bp_coefficients"]]
    )  # ~10s
    rp_coeffs = np.array(
        [literal_eval(coeffs) for coeffs in xp_spectra_table["rp_coefficients"]]
    )
    xp_coeffs = np.concatenate((bp_coeffs, rp_coeffs), axis=1)

    bp_errs = np.array(
        [literal_eval(errs) for errs in xp_spectra_table["bp_coefficient_errors"]]
    )
    rp_errs = np.array(
        [literal_eval(errs) for errs in xp_spectra_table["rp_coefficient_errors"]]
    )
    xp_errs = np.concatenate((bp_errs, rp_errs), axis=1)

    return gaia_ids, xp_coeffs, xp_errs


WLEN_GRID = np.arange(336, 1021, 2)


def sample_xp_spectra(filename, wlen_grid=WLEN_GRID):
    """
    Converts a .csv file containing XP coefficients (and errors) to numpy arrays
     containing the spectra sampled at the given wavelengths
    Returns:
    - gaia_ids: The Gaia EDR3 IDs (N,)
    - fluxes: The spectra (N, len(wlen_grid))
    - flux_errs: The errors on the spectra (N, len(wlen_grid))
    """
    print("Reading table...")
    calibrated_df, _ = calibrate(filename, sampling=wlen_grid, save_file=False)

    ids_ = calibrated_df["source_id"].values
    fluxes_ = np.array(calibrated_df["flux"].values.tolist())
    flux_errs_ = np.array(calibrated_df["flux_error"].values.tolist())

    return ids_, fluxes_, flux_errs_


if __name__ == "__main__":
    XP_FILE = "../data/external/xp.csv"

    print("Extracting XP coefficients...")
    ids, xp, xp_err = read_xp_to_arrays(XP_FILE)
    np.savez_compressed(
        "../data/interim/xp_coeffs.npz",
        ids=ids,
        xp=xp,
        xp_err=xp_err,
    )

    print("Sampling XP spectra...")
    ids, fluxes, flux_errs = sample_xp_spectra(XP_FILE)
    np.savez_compressed(
        "../data/interim/xp_spectra.npz",
        ids=ids,
        wlen=WLEN_GRID,
        fluxes=fluxes,
        flux_errs=flux_errs,
    )
