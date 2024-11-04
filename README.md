# wd_xp_methods
A comparison of different methods for analysing Gaia XP spectra of white dwarfs, particularly to find polluted WDs

---

## Plan

1. Assemble dataset. We'll just use the following constraints:
    1. $$
\mathtt{phot\_xp\_n\_obs} \geq \begin{cases}
10 & \mathtt{x}=\mathtt{r}\\
15 & \mathtt{x}=\mathtt{b}
\end{cases}
$$ (Andrae+23, GSP-Phot)
    2. $$
\mathtt{visibility\_periods\_used} \geq 10
$$ (Lindegren+18)

and that's it.

    1. Construct SQL query to use in TOPCAT on GF+21
    2. Write it up somewhere, later in the README perhaps

2. Obtain the XP spectra for this sample
    1. Download from Gaia@AIP?
    2. Find out how PC+24 did it pythonically?

3. Apply / reproduce methods

    1. UMAP (Kao+24)
    2. tSNE
    3. Contrastive Learning
    4. SOMs (PC+24)
    5. Standard ML (Vincent+24)

---

## Data selection

### Sample from GF+21

The following SQL query was used for sample selection from Gaia EDR3. To obtain the data we used TOPCAT to post the following query to the VizieR dataset `J/MNRAS/508/3877/maincat` (the main catalogue of Gentile Fusillo+21, hereafter GF+21)

```sql
SELECT
    WDJname, GaiaEDR3,
    RA_ICRS, DE_ICRS, Plx,
    "Gmag", BPmag, RPmag,  -- "Gmag" to avoid confusion with GMAG
    o_BPmag, o_RPmag  -- phot_xp_n_obs
    Nper,             -- visibility_periods_used
    RUWE, Pwd, TeffH,
    RFBP, RFRP        -- integrated XP flux over error
FROM "J/MNRAS/508/3877/maincat"
WHERE
    o_BPmag >= 10 AND -- phot_bp_n_obs (Andrae+23)
    o_RPmag >= 15 AND -- phot_rp_n_obs (")
    Nper >= 10        -- visibility_periods_used (Lindegren+18)
```
Save the resulting table to `./src/data/external/gf21.csv`.

We also obtain a subset of this for which a spectral classification exists

1. Use MWDD?
2. Use GF+21's other catalogue?

---
## References

Gentile Fusillo+24
Kao+24
Perez-Couto+24
Vincent+24