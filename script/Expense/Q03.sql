-- from Q03: this will miss about 66981
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


 
-- from R20: exclude 66981
SELECT
    CASE
        WHEN hdr.business_unit LIKE 'E%' THEN 'APE'
        WHEN REGEXP_LIKE(hdr.business_unit, '^(CO|DS|PV|PT)') THEN 'Sub-national'
        WHEN NOT REGEXP_LIKE(hdr.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') THEN 'National'
        ELSE 'Unmapped'
    END AS gov_level,
    SUM(line.monetary_amount) AS implementation
FROM PS_JRNL_HEADER hdr
JOIN PS_JRNL_LN line
  ON hdr.business_unit = line.business_unit
 AND hdr.journal_id = line.journal_id
 AND hdr.journal_date = line.journal_date
 AND hdr.unpost_seq = line.unpost_seq
WHERE hdr.unpost_seq = 0
  AND hdr.fiscal_year = 2025
  AND hdr.accounting_period BETWEEN 1 AND 12
  AND hdr.jrnl_hdr_status = 'P'
  AND line.jrnl_line_source <> 'CLO'
  AND (
        (SUBSTR(line.account, 1, 2) IN ('27', '50')
         AND line.jrnl_line_source NOT IN ('GAR', 'PNL', 'SCP'))
        OR SUBSTR(line.account, 1, 2) NOT IN ('27', '50')
      )
  AND hdr.journal_id NOT IN ('0002249795', '0002251264')
  AND (
        line.account LIKE '2%'
        OR line.account LIKE '6%'
        OR line.account LIKE '7009%'
      )
and line.account not like '66981'
GROUP BY
    CASE
        WHEN hdr.business_unit LIKE 'E%' THEN 'APE'
        WHEN REGEXP_LIKE(hdr.business_unit, '^(CO|DS|PV|PT)') THEN 'Sub-national'
        WHEN NOT REGEXP_LIKE(hdr.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') THEN 'National'
        ELSE 'Unmapped'
    END
ORDER BY gov_level;