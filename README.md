# wd_xp_methods
A comparison of different methods for analysing Gaia XP spectra of white dwarfs, particularly to find polluted WDs

## Data Collection

### Obtaining WD candidate sample

To obtain a good sample of WDs whose XP spectra to analyse, we use the query in `src/queries/gf21.sql` to obtain data from the catalogue of Gentile Fusillo+21 (hereafter GF+21).
This query uses similar selection criteria to Pérez-Couto+24 (PC+24):

1. 1. `phot_bp_n_obs` >= 10  (Andrae+23)
   2. `phot_rp_n_obs` >= 15  (ibid.)
2. `visibility_periods_used` >= 10  (Lindegren+18)

We used TOPCAT to obtain the interim sample, which is saved to `data/interim/gf21_filtered.csv` and contains 1 070 932 rows.

#### Obtaining XP spectra

We now obtain the XP spectra for the those objects which actually have available XP spectra.
These are obtained by uploading a VOtable of the WDs' Gaia DR3 IDs to https://gaia.aip.de/query/
The VOtable is created by `scripts/make_gf21_votable.py`, which creates the file `data/interim/gf21_ids.xml`.

Upload this .xml file to Gaia@AIP at the above link under 'Upload VOTable' (NB: you probably need an account), and name it gf21_filtered.
It should then appear in the 'Job list' panel, and finish uploading after about a minute.
Copy the query in `src/queries/gaia_aip_xp.sql` into the SQL query box, making sure to replace `<username>` with your actual username.
Change the Table name field to `xp`, and change the Queue time to 5 minutes.
When I do this, it takes about 50 seconds to complete the join.

After the job is complete, click the Download tab and download the csv file (which may a minute or two to assemble as the table is about 4GB).
Save the file to `data/external/xp.csv`.
It should have 107 164 rows, one for every WD candidate with available Gaia XP spectra.

Now that we have the XP coefficients downloaded, we need to get them into a nicer form than a .csv file.
This is achieved by the `process_xp.py` program, which stores the XP coefficients in the file `data/interim/xp_coeffs.npz`. This file contains:
- `ids` -- the Gaia EDR3 IDs
- `xp` -- the XP coefficients
- `xp_err` -- the errors on the XP coefficients

This file also contains a function (`sample_xp_spectra`) to convert the XP coefficients to ordinary, flux-vs-wavelength spectra, using the `GaiaXPy` package (Gaia Collaboration, Montegriffo+22).


### Getting datasets for pollution labelling

We use three datasets to label our knowledge of the pollution of WDs. These are:
- GF+21's Gaia-SDSS spectroscopic sample (Gaia+SDSS; GF+21);
- Montreal White Dwarf Database (MWDD; Dufour+17);
- Planetary-Enriched White Dwarf Database (PEWDD; Williams+24);

These datasets, containing spectral classifications of $10^3$-$10^5$ WDs, are used to label WDs as "known polluted" (1), "known non-polluted" (0), or "unknown" (-1).
"Known polluted" means that at least one of the datasets identifies the WD as polluted. 
"Known non-polluted" means that at least one of the datasets identifies the WD as something else, e.g. a DA.
"Unknown" means that the WD is not in any of the above datasets

The datasets are obtained by, respectively:
- GF21xSDSS: Submit the query `queries/gf21_sdss.sql`, to e.g. TOPCAT;
- MWDD: Visit montrealwhitedwarfdatabase.org. On the 'Tables and Charts' page, click the 'Options' button and deselect everything except 'Gaia DR3 ID' and 'Spectral type'. Click 'Export as csv'. Last accessed 2024-11-06.
- PEWDD: The dataset can be downloaded from https://github.com/jamietwilliams/PEWDD/blob/main/PEWDD.csv . Last accessed 2024-11-06.

The datasets are stored in `data/external/evaluation` as `gf21_sdss.csv`, `mwdd.csv`, and `pewdd.csv`.

GF21xSDSS is a stable VizieR catalogue (J/MNRAS/508/3877/sdssspec), but the other two catalogues are actively updated. For reproducibility, these are saved here as they were on Nov 6 2024.


## Investigations

### Applying $t$SNE 

The program `scripts/umap_tsne_xp.py` runs UMAP and tSNE on the sample's XP spectra.
Some preprocessor functions are found in `scripts/preprocessors.py`, including normalising by the G flux (as in Kao+24) or by the L2 norm (as in PC+24).
The results don't seem to be affected very strongly by the normalisation chosen; we use the G flux normalisation in our work.

The UMAP and $t$SNE embeddings of the XP spectra can be found in `data/processed/umap_xp.npz` and `tsne_xp.npz`.
The $t$SNE embedding contains two islands with a high proportion of confirmed polluted WDs.
The members of these islands are decided objectively using DBSCAN (Ester+96), which is applied by `scripts/isolate_polluted_islands.py`.

### Comparing previous methods

The classifications of García-Zamora+25 and Vincent+24 are, commendably, available online at the VizieR catalogues 'J/A+A/699/A3/table3' and 'J/A+A/682/A5/catalog' respectively. The queries
```sql
SELECT GaiaEDR3, SPPred
FROM "J/A+A/699/A3/table3"
```
and
```sql
SELECT GaiaDR3, SpType
FROM "J/A+A/682/A5/catalog"
```
grab the IDs and classifications for all of the WDs in their respective samples. These queries can be given to e.g. TOPCAT.
The resulting datasets should be stored under `data/external/previous_work`.

The WDs selected by Kao+24 are not publicly available as they are subject to an ongoing spectroscopic follow-up programme.
However, these were communicated by personal communication, and stored in `data/external/previous_work/secret` and `.gitignore`d to ensure propriety.

The selections of Pérez-Couto+24 are also not publicly available, though we were able to approximately reproduce their findings.
Again, to ensure propriety, the script reproducing their results is `.gitignore`d.


### The split in the polluted islands

$t$SNE identifies two islands of polluted WDs, rather than one.
The reasons for this are revealed by running $t$SNE on the polluted candidates plus a small fraction of the other objects.
This is carried out by `divide_polluted_islands.py`, which creates the relevant embeddings.


## Creating figures

Scripts used to create figures in the paper (some of which rely on non-public data, see above) are found in `scripts/create_fig{x}_{figname}.py`



## References

Andrae+23
Dufour+17
Ester+96
Gaia Collaboration, Montegriffo+22
García-Zamora+25
Gentile Fusillo+24
Kao+24
Lindegren+18
Perez-Couto+24
Vincent+24
Williams+24