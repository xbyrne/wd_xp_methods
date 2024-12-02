# wd_xp_methods
A comparison of different methods for analysing Gaia XP spectra of white dwarfs, particularly to find polluted WDs


## Plan

1. Assemble dataset from GF+21 [x]

2. Obtain the XP spectra for this sample from Gaia@AIP [x]

3. Apply / reproduce methods []

    1. UMAP (Kao+24) [x]
    2. tSNE [x]
    3. Contrastive Learning []
        1. Work out noising -- do we really want to resample using the errors from 10^5 objects? Are there any alternatives?
    4. SOMs (PC+24) []
        1. Ask PC whether they tried just using one SOM?
        2. Any advice for hyperparameter optimisation?
    5. Standard ML (Vincent+24) []
        1. Grab his network somehow?
        2. Reproduce?


## Evaluating previous methods against available datasets

We first evaluate the results of others' attempts to select polluted WDs from Gaia XP spectra, by comparing them to datasets of spectroscopically-confirmed polluted WDs.

### Getting datasets for pollution labelling

We use three datasets to label the pollution of WDs. These are:
- Gentile Fusillo+21's Gaia-SDSS spectroscopic sample (GF21xSDSS; Gentile Fusillo+21);
- Montreal White Dwarf Database (MWDD; Dufour+17);
- Planetary-Enriched White Dwarf Database (PEWDD; Williams+24);

These datasets, containing spectral classifications of $10^3$-$10^5$ WDs, are used to label WDs as "polluted" (1), "not polluted" (0), or "unknown" (-1). "Polluted" means that at least one of the datasets identifies the WD as polluted. "Not polluted" means that at least one of the datasets identifies the WD as something else, e.g. a DA, and none of them identify it as polluted. 

The datasets are obtained by, respectively:
- GF21xSDSS: Submit the query `queries/gf21_sdss.sql`, to e.g. TOPCAT;
- MWDD: Visit montrealwhitedwarfdatabase.org. On the 'Tables and Charts' page, click the 'Options' button and deselect everything except 'Gaia DR3 ID' and 'Spectral type'. Click 'Export as csv'.
- PEWDD: The dataset can be downloaded from https://github.com/jamietwilliams/PEWDD/blob/main/PEWDD.csv

The datasets are stored in `data/external/evaluation` as `gf21_sdss.csv`, `mwdd.csv`, and `pewdd.csv`.

GF21xSDSS is a stable VizieR catalogue (J/MNRAS/508/3877/sdssspec), but the other two catalogues are actively updated. For reproducibility, these are saved here as they were on Nov 6 2024.

### Datasets produced in previous work

The classifications of García-Zamora+23 and Vincent+24 are, commendably, available online at the VizieR catalogues 'J/A+A/679/A127/catalog' and 'J/A+A/682/A5/catalog' respectively. The queries
```sql
SELECT GaiaDR3, SPPred
FROM "J/A+A/679/A127/catalog"
```
and
```sql
SELECT GaiaDR3, SpType
FROM "J/A+A/682/A5/catalog"
```
grab the IDs and classifications for all of the WDs in their respective samples. These queries can be given to e.g. TOPCAT. The resulting datasets should be stored under `data/external/previous_work`.

Due to ongoing spectroscopic follow-up surveys, and likely an understandable fear of being poached, the WDs selected by the methods of Kao+24 and Pérez-Couto+24 are not publicly available. Kao+24 do publish the UMAP coordinates of their entire sample (J/ApJ/970/181/catalog), though their selection of in this space of 465 WDs is not public. The 465 WDs have, however, been obtained by personal communication and can hence be evaluated. These are stored in `data/external/previous_work/secret`, which is gitignored to ensure propriety.

### Evaluating previous methods

The program `scripts/evaluate_existing_methods.py` contains a function `check_whether_obj_polluted`, which checks a given Gaia DR3 ID against these three databases. This function returns 1 / 0 / -1, according to whether the WD has been classified as polluted:
    - 1: The object has been classified as polluted in any of the three datasets
    - 0: None of the datasets classify the object as polluted (unless any do).
    - -1: It is *possible* that the object is polluted, but not confirmed.

NB: It is possible that some WDs labelled as not polluted are, in fact, polluted, as the spectra obtained to assign the class in the dataset may not be of sufficiently high resolution to identify metal lines. However, the resolution of the Gaia XP spectra is likely to be even worse, so if something is unpolluted to the level of the spectral classifications in the datasets, pollution will certainly be undetectable in the XP spectra.

The details of how these cases are ascertained (e.g. which classifications are included) are given in the docstrings of the `check_{dataset}` functions.

Running the script `scripts/evaluate_existing_methods.py` outputs the numbers of polluted/non-polluted/unknown WDs claimed by each of the previous works to be polluted. The program still runs if the Kao+24 selection is not available.


## Data selection

### Obtaining WD candidate sample

To obtain a good sample of WDs whose XP spectra to analyse, we use the query in `src/queries/gf21.sql` to obtain data from the catalogue of Gentile Fusillo+21 (hereafter GF+21). This query uses similar selection criteria to PC+24.:

1. 1. `phot_bp_n_obs` >= 10  (Andrae+23)
   2. `phot_rp_n_obs` >= 15  (^)
2. `visibility_periods_used` >= 10  (Lindegren+18)

We used TOPCAT to obtain the interim sample, which is saved to `data/interim/gf21_filtered.csv` and contains 1 070 932 rows.


### Obtaining XP spectra for sample

We now obtain the XP spectra for the subset of those objects which actually have available spectra yet. Visiting https://gaia.aip.de/query/, we must first upload a VOtable. This is created by `scripts/make_gf21_votable.py`, which creates the file `data/interim/gf21_ids.xml`.

Upload this .xml file to Gaia@AIP at the above link under 'Upload VOTable' (NB: you probably need an account), and name it gf21_filtered. It should then appear in the 'Job list' panel, and finish uploading after about a minute. Copy the query in `src/queries/gaia_aip_xp.sql` into the SQL query box, making sure to replace `<username>` with your actual username. Change the Table name field to `xp`, and change the Queue time to 5 minutes. When I do this, it takes about 50 seconds to complete the join.

After the job is complete, click the Download tab and download the csv file (which may a minute or two to assemble as the table is about 4GB). Save the file to `data/external/xp.csv`. It should have 107 164 rows, one for every WD candidate with available Gaia XP spectra.

### Process XP spectra

Now that we have the XP coefficients downloaded, we need to get them into a nicer form than a .csv file.
This is achieved by the `process_xp.py` program, which creates two .npz files:
1. `data/interim/xp_coefficients.npz`
    - `ids` -- the Gaia EDR3 IDs
    - `xp` -- the XP coefficients
    - `xp_err` -- the errors on the XP coefficients
2. `data/interim/xp_sampledspectra.npz`
    - `ids` -- "
    - `wlen` -- wavelengths at which the spectra are sampled
    - `flux` -- flux in the spectrum

The latter makes use of the `GaiaXPy` package (Gaia Collaboration, Montegriffo+22).


#### TODO: upload the data/external folder to zenodo when project done.


## Applying methods

### UMAP & tSNE

The program `scripts/umap_tsne_xp.py` runs UMAP and tSNE on the sample's XP spectra. A couple of data normalisation methods are found in the `scripts/preprocessors.py` file, including normalising by the G flux (as in Kao+24) or by the L2 norm (as in PC+24). The results don't seem to be affected very strongly by the normalisation chosen.

The UMAP and tSNE embeddings of the XP spectra an be found in `data/processed/umap_xp.npz` and `tsne_xp.npz`.


## References

Andrae+23
Dufour+17
Gaia Collaboration, Montegriffo+22
Gentile Fusillo+24
Kao+24
Lindegren+18
Perez-Couto+24
Vincent+24
Williams+24