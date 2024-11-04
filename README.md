# wd_xp_methods
A comparison of different methods for analysing Gaia XP spectra of white dwarfs, particularly to find polluted WDs

---

## Plan

1. Assemble dataset from GF+21 [x]

2. Obtain the XP spectra for this sample from Gaia@AIP

3. Apply / reproduce methods

    1. UMAP (Kao+24)
    2. tSNE
    3. Contrastive Learning
    4. SOMs (PC+24)
    5. Standard ML (Vincent+24)

---

## Data selection

### Obtaining WD candidate sample from GF+21

To obtain a good sample of WDs whose XP spectra to analyse, we use the query in `src/queries/gf21.sql` to obtain data from the catalogue of Gentile Fusillo+24 (hereafter GF+24). This query uses similar selection criteria to PC+24, but is slightly more inclusive:

1. $$
\mathtt{phot\_xp\_n\_obs} \geq \begin{cases}
10 & \mathtt{x}=\mathtt{r}\\
15 & \mathtt{x}=\mathtt{b}
\end{cases}
$$ (Andrae+23, GSP-Phot)
2. $$
\mathtt{visibility\_periods\_used} \geq 10
$$ (Lindegren+18)

We used TOPCAT to obtain the sample, which is saved to `data/external/gf21.csv` and contains 1 070 932 rows. Most of these objects will not have XP spectra, however...


### Obtaining XP spectra for sample

We now obtain the XP spectra for those objects -- at least, the ones which _have_ XP spectra yet. Visiting https://gaia.aip.de/query/, we must first upload a VOtable. This is carried out by `src/scripts/make_gf21_votable.py`, which creates the file `src/data/interim/gf21_ids.xml`



We also obtain a subset of this for which a spectral classification exists

1. Use MWDD?
2. Use GF+21's other catalogue?

---
## References

Andrae+23
Gentile Fusillo+24
Kao+24
Lindegren+18
Perez-Couto+24
Vincent+24