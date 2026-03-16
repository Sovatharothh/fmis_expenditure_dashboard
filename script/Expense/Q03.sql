SELECT
    CASE
        WHEN a.business_unit LIKE 'E%' THEN 'APE'
        WHEN REGEXP_LIKE(a.business_unit, '^(CO|DS|PV|PT)') THEN 'Sub-national'
        WHEN NOT REGEXP_LIKE(a.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') THEN 'National'
    END AS gov_level,
    SUM(a.monetary_amount) AS implementation
FROM PS_Z_Q03_QRY_VW a
WHERE a.accounting_dt >= DATE '2025-01-01'
  AND a.accounting_dt <= DATE '2025-12-31'
  AND a.budget_ref LIKE '2025%'
  AND a.budget_ref NOT LIKE 'SD%'
  AND a.post_status_ap = 'P'
  AND a.gl_distrib_status = 'D'
  AND (a.account LIKE '2%' OR a.account LIKE '6%' OR a.account LIKE '70091')
GROUP BY
    CASE
        WHEN a.business_unit LIKE 'E%' THEN 'APE'
        WHEN REGEXP_LIKE(a.business_unit, '^(CO|DS|PV|PT)') THEN 'Sub-national'
        WHEN NOT REGEXP_LIKE(a.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') THEN 'National'
    END
ORDER BY gov_level;