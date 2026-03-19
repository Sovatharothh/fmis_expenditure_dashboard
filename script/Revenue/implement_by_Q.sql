SELECT
    CASE 
        WHEN hdr.accounting_period BETWEEN 1 AND 3 THEN 'Q1'
        WHEN hdr.accounting_period BETWEEN 4 AND 6 THEN 'Q2'
        WHEN hdr.accounting_period BETWEEN 7 AND 9 THEN 'Q3'
        WHEN hdr.accounting_period BETWEEN 10 AND 12 THEN 'Q4'
        ELSE 'Other'
    END AS quarter_name,
    SUM(line.monetary_amount) * -1 AS quarterly_implementation
FROM PS_JRNL_HEADER hdr
JOIN PS_JRNL_LN line
  ON hdr.business_unit = line.business_unit
 AND hdr.journal_id    = line.journal_id
 AND hdr.journal_date  = line.journal_date
 AND hdr.unpost_seq    = line.unpost_seq
WHERE hdr.unpost_seq = 0
  AND hdr.fiscal_year = 2026
  AND hdr.accounting_period BETWEEN 1 AND 12
  AND hdr.jrnl_hdr_status = 'P'
  AND line.jrnl_line_source <> 'CLO'
    and ( REGEXP_LIKE(hdr.business_unit, '^(CO|DS|PV|PT)') or
        NOT REGEXP_LIKE(hdr.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') )
  
  -- Revenue filter based on your image ranges (Tax, Non-Tax, Customs)

  AND (
       (line.account BETWEEN '7001' AND '7199') 
    OR (line.account BETWEEN '7200' AND '77981')
  )
  
  -- Specific exclusion for the high-value internal account
  AND line.account NOT LIKE '76061%'

GROUP BY
    CASE 
        WHEN hdr.accounting_period BETWEEN 1 AND 3 THEN 'Q1'
        WHEN hdr.accounting_period BETWEEN 4 AND 6 THEN 'Q2'
        WHEN hdr.accounting_period BETWEEN 7 AND 9 THEN 'Q3'
        WHEN hdr.accounting_period BETWEEN 10 AND 12 THEN 'Q4'
        ELSE 'Other'
    END
ORDER BY 
    quarter_name;