# wd_xp_methods
A comparison of different methods for analysing Gaia XP spectra of white dwarfs, particularly to find polluted WDs

---

## Plan

1. Assemble dataset (let's use the set union of those used by Kao+24, Perez-Couto+24, and Vincent+24)

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

### Sample from GF+24

The following SQL query was used for data collection. We used TOPCAT on the VizieR dataset J/MNRAS/...

```sql
SELECT
...
```

We also obtain a subset of this for which a spectral classification exists

1. Use MWDD?
2. Use GF+21's other catalogue?

---
## References

Gentile Fusillo+24
Kao+24
Perez-Couto+24
Vincent+24