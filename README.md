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


## Data selection

### Obtaining WD candidate sample from GF+21

To obtain a good sample of WDs whose XP spectra to analyse, we use the query in `src/queries/gf21.sql` to obtain data from the catalogue of Gentile Fusillo+21 (hereafter GF+21). This query uses similar selection criteria to PC+24, but is slightly more inclusive:

1. 1. `phot_bp_n_obs` >= 10  (Andrae+23)
   2. `phot_rp_n_obs` >= 15  (^)
2. `visibility_periods_used` >= 10  (Lindegren+18)

We used TOPCAT to obtain the sample, which is saved to `data/external/gf21.csv` and contains 1 070 932 rows. Most of these objects will not have XP spectra, however...


### Obtaining XP spectra for sample

We now obtain the XP spectra for those objects -- at least, the ones which _have_ XP spectra yet. Visiting https://gaia.aip.de/query/, we must first upload a VOtable. This is carried out by `scripts/make_gf21_votable.py`, which creates the file `data/interim/gf21_ids.xml`.

Upload this .xml file to Gaia@AIP at the above link under 'Upload VOTable' (NB: you probably need an account), and name it gf21_ids. It should then appear in the 'Job list' panel. Copy the query in `src/queries/gaia_aip_xp.sql` into the SQL query box, making sure to replace `<username>` with your actual username. Change the Table name field to gf21_xp, and change the Queue time to 5 minutes. When I do this, it takes about 50 seconds to complete the join.

After the job is complete, click the Download tab and download the csv file (which may a minute or two to assemble as the table is a few GB). Save the file to `data/external/gf21_xp.csv`.

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

### Obtaining a labelled subset of the WD spectral classes

Gentile Fusillo+21 also visually classify ~40k WD spectra in SDSS which have a match in the main GF21 catalogue. This can be downloaded from TOPCAT as with the main catalogue, using the short query in `queries/gf21_sdss.sql`. The resulting dataset, containing just two columns -- Gaia EDR3 IDs and spectral class -- is stored in `data/external/gf21_sdss.csv`.

We also download the Montreal White Dwarf Database (MWDD; Dufour+17; www.montrealwhitedwarfdatabase.org). On the 'Tables and Charts' page, click the 'Options' button and deselect everything except 'Gaia DR3 ID' and 'Spectral type'. Click 'Export as csv' and save to `data/external/mwdd.csv`.

Finally, we also download the Planetary Enriched White Dwarf Database (PEWDD; Williams+24) to potentially label more WDs as polluted. This is downloaded by the `scripts/download_pewdd.py` program, which saves the database to `data/external/pewdd.csv`.

The program `scripts/check_known_polluted.py` checks all the sources in the sample against these three databases, assembling the dataset `data/interim/is_polluted.csv`. This table contains two columns:
- The EDR3 ID;
- 1 / 0 / -1, according to whether the WD has been classified as polluted:
    - 1: The object has been classified as polluted in any of the three datasets
    - 0: None of the datasets classify the object as polluted (unless any do)
    - -1: It is *possible* that the object is polluted, but not confirmed.

The details of how these cases are ascertained are given in the docstrings of the `check_{dataset}` functions. The dataset `is_polluted.csv` contains 858 (0.8%) known polluted WDs, 12638 (11.8%) known *un*-polluted WDs, and 93668 (87.4%) whose classification is uncertain.


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