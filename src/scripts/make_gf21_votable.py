"""
make_gf21_votable.py
====================
Converts the GF21 sample to a VOtable for upload to Gaia@AIP, to get the XP coefficients.
All we need is the Gaia EDR3 IDs, so to save space that's all we'll keep.
"""

import pandas as pd
from astropy.table import Table


def make_votable(df):
    """
    Converts a df containing a column `GaiaEDR3` to a VOtable
    containing only this column.
    """
    ids = df["GaiaEDR3"].to_frame()
    return Table.from_pandas(ids)


if __name__ == "__main__":
    gf21 = pd.read_csv("../data/external/gf21.csv")
    table = make_votable(gf21)
    table.write("../data/interim/gf21_ids.xml", format="votable", overwrite=True)
