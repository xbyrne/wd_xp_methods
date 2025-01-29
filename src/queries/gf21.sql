-- gf21.sql
-- Query to obtain the GF+21 catalog from the VizieR service
-- We used TOPCAT to post the query and download the results
-- The resulting table should be saved to `src/data/interim/gf21_filtered.csv`

SELECT GaiaEDR3, "Gmag", BPmag, RPmag, RA_ICRS, DE_ICRS, Plx, Pwd, TeffH, SDSS12
FROM "J/MNRAS/508/3877/maincat"
WHERE
    o_BPmag >= 10 AND -- phot_bp_n_obs (Andrae+23)
    o_RPmag >= 15 AND -- phot_rp_n_obs (")
    Nper >= 10        -- visibility_periods_used (Lindegren+18)