SELECT
    CASE
        WHEN a.business_unit LIKE 'E%' THEN 'APE'
        WHEN REGEXP_LIKE(a.business_unit, '^(CO|DS|PV|PT)') THEN 'Sub-national'
        WHEN NOT REGEXP_LIKE(a.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') THEN 'National'
    END
ORDER BY gov_level;
    SUM(line.monetary_amount) * -1 AS implementation
FROM PS_JRNL_HEADER hdr,
     PS_JRNL_LN line
WHERE hdr.business_unit = line.business_unit
  AND hdr.journal_id    = line.journal_id
  AND hdr.journal_date  = line.journal_date
  AND hdr.unpost_seq    = line.unpost_seq
  AND hdr.unpost_seq = 0
  AND hdr.fiscal_year = 2025
  AND hdr.accounting_period BETWEEN 1 AND 12
  AND hdr.jrnl_hdr_status = 'P'
  AND line.jrnl_line_source <> 'CLO'
  AND (line.account LIKE '7%' OR line.account not LIKE '76061%')
GROUP BY
    CASE
        WHEN a.business_unit LIKE 'E%' THEN 'APE'
        WHEN REGEXP_LIKE(a.business_unit, '^(CO|DS|PV|PT)') THEN 'Sub-national'
        WHEN NOT REGEXP_LIKE(a.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') THEN 'National'
    END
ORDER BY gov_level;