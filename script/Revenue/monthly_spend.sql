SELECT
    CASE 
        WHEN hdr.accounting_period = 1 THEN 'Jan'
        WHEN hdr.accounting_period = 2 THEN 'Feb'
        WHEN hdr.accounting_period = 3 THEN 'Mar'
        WHEN hdr.accounting_period = 4 THEN 'Apr'
        WHEN hdr.accounting_period = 5 THEN 'May'
        WHEN hdr.accounting_period = 6 THEN 'Jun'
        WHEN hdr.accounting_period = 7 THEN 'Jul'
        WHEN hdr.accounting_period = 8 THEN 'Aug'
        WHEN hdr.accounting_period = 9 THEN 'Sep'
        WHEN hdr.accounting_period = 10 THEN 'Oct'
        WHEN hdr.accounting_period = 11 THEN 'Nov'
        WHEN hdr.accounting_period = 12 THEN 'Dec'
        ELSE 'Other'
    END AS month_name,
    SUM(line.monetary_amount) * -1 AS monthly_implementation
FROM PS_JRNL_HEADER hdr
JOIN PS_JRNL_LN line
  ON hdr.business_unit = line.business_unit
 AND hdr.journal_id    = line.journal_id
 AND hdr.journal_date  = line.journal_date
 AND hdr.unpost_seq    = line.unpost_seq
WHERE hdr.unpost_seq = 0
  AND hdr.fiscal_year = 2026
  and ( REGEXP_LIKE(hdr.business_unit, '^(CO|DS|PV|PT)') or
        NOT REGEXP_LIKE(hdr.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') )
  AND hdr.accounting_period BETWEEN 1 AND 12
  AND hdr.jrnl_hdr_status = 'P'
  AND line.jrnl_line_source <> 'CLO'
  
  -- Revenue filter based on your image ranges (Tax, Non-Tax, Customs)

  AND (
       (line.account BETWEEN '7001' AND '7199') 
    OR (line.account BETWEEN '7200' AND '77981')
  )
  
  -- Specific exclusion for the high-value internal account
  AND line.account NOT LIKE '76061%'

GROUP BY
    hdr.accounting_period,
    CASE 
        WHEN hdr.accounting_period = 1 THEN 'Jan'
        WHEN hdr.accounting_period = 2 THEN 'Feb'
        WHEN hdr.accounting_period = 3 THEN 'Mar'
        WHEN hdr.accounting_period = 4 THEN 'Apr'
        WHEN hdr.accounting_period = 5 THEN 'May'
        WHEN hdr.accounting_period = 6 THEN 'Jun'
        WHEN hdr.accounting_period = 7 THEN 'Jul'
        WHEN hdr.accounting_period = 8 THEN 'Aug'
        WHEN hdr.accounting_period = 9 THEN 'Sep'
        WHEN hdr.accounting_period = 10 THEN 'Oct'
        WHEN hdr.accounting_period = 11 THEN 'Nov'
        WHEN hdr.accounting_period = 12 THEN 'Dec'
        ELSE 'Other'
    END
ORDER BY 
    hdr.accounting_period;