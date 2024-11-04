-- gaia_aip_xp.sql
-- Query to obtain the XP coefficients (and auxiliary data)
--  of the sources in the GF+21 catalogue
-- To be uploaded to the Gaia@AIP interface (https://gaia.aip.de/query/)

SELECT
    source_id,
    bp_coefficients, rp_coefficients,
    bp_coefficient_errors, rp_coefficient_errors,
    bp_coefficient_correlations, rp_coefficient_correlations,
    bp_n_parameters, bp_standard_deviation,
    rp_n_parameters, rp_standard_deviation
FROM
	gaiadr3.xp_continuous_mean_spectrum as xp
JOIN
	gaia_user_<username>.gf21_ids as wds
--    Replace ^^^^^^^^^^ with your username
ON
	xp.source_id = wds."GaiaEDR3"