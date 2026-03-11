SELECT
    CASE
        WHEN line.business_unit LIKE 'E%' THEN 'APE'
        WHEN NOT REGEXP_LIKE(line.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') THEN 'National'
        ELSE 'Sub-national'
    END AS gov_level,
    SUM(line.monetary_amount) * -1 AS implementation
FROM PS_JRNL_HEADER hdr,
     PS_JRNL_LN line
WHERE hdr.business_unit = line.business_unit
  AND hdr.journal_id    = line.journal_id
  AND hdr.journal_date  = line.journal_date
  AND hdr.unpost_seq    = line.unpost_seq
  AND hdr.unpost_seq = 0
  AND hdr.fiscal_year = 2026
  AND hdr.accounting_period BETWEEN 1 AND 12
  AND hdr.jrnl_hdr_status = 'P'
  AND line.jrnl_line_source <> 'CLO'
  AND (line.account LIKE '2%' OR line.account LIKE '7%')
GROUP BY
    CASE
        WHEN line.business_unit LIKE 'E%' THEN 'APE'
        WHEN NOT REGEXP_LIKE(line.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') THEN 'National'
        ELSE 'Sub-national'
    END
ORDER BY gov_level