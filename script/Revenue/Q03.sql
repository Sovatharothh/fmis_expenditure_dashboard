SELECT
    CASE
        WHEN hdr.business_unit LIKE 'E%' THEN 'APE'
        WHEN REGEXP_LIKE(hdr.business_unit, '^(CO|DS|PV|PT)') THEN 'Sub-national'
        WHEN NOT REGEXP_LIKE(hdr.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') THEN 'National'
        ELSE 'Unmapped'
    END AS gov_level,
    SUM(line.monetary_amount) * -1 AS implementation
FROM PS_JRNL_HEADER hdr
JOIN PS_JRNL_LN line
  ON hdr.business_unit = line.business_unit
 AND hdr.journal_id    = line.journal_id
 AND hdr.journal_date  = line.journal_date
 AND hdr.unpost_seq    = line.unpost_seq
WHERE hdr.unpost_seq = 0
  AND hdr.fiscal_year = 2025
  AND hdr.accounting_period BETWEEN 1 AND 12
  AND hdr.jrnl_hdr_status = 'P'
  AND line.jrnl_line_source <> 'CLO'
  -- Filter: Accounts starting with 7, but excluding those starting with 76061
  AND line.account LIKE '7%'
  AND line.account NOT LIKE '76061%'
GROUP BY
    CASE
        WHEN hdr.business_unit LIKE 'E%' THEN 'APE'
        WHEN REGEXP_LIKE(hdr.business_unit, '^(CO|DS|PV|PT)') THEN 'Sub-national'
        WHEN NOT REGEXP_LIKE(hdr.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') THEN 'National'
        ELSE 'Unmapped'
    END
ORDER BY 
    CASE 
        WHEN gov_level = 'National' THEN 1 
        WHEN gov_level = 'Sub-national' THEN 2 
        WHEN gov_level = 'APE' THEN 3 
        ELSE 4 
    END;


-- implemenation by gov_level and modifed law
SELECT
    CASE
        WHEN hdr.business_unit LIKE 'E%' THEN 'APE'
        WHEN REGEXP_LIKE(hdr.business_unit, '^(CO|DS|PV|PT)') THEN 'Sub-national'
        WHEN NOT REGEXP_LIKE(hdr.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') THEN 'National'
        ELSE 'Unmapped'
    END AS gov_level,
    SUM(line.monetary_amount) * -1 AS implementation
FROM PS_JRNL_HEADER hdr
JOIN PS_JRNL_LN line
  ON hdr.business_unit = line.business_unit
 AND hdr.journal_id    = line.journal_id
 AND hdr.journal_date  = line.journal_date
 AND hdr.unpost_seq    = line.unpost_seq
WHERE hdr.unpost_seq = 0
  AND hdr.fiscal_year = 2025
  AND hdr.accounting_period BETWEEN 1 AND 12
  AND hdr.jrnl_hdr_status = 'P'
  AND line.jrnl_line_source <> 'CLO'
  
  -- Use the specific ranges from your R20_1.2.1.1.1 tree
  AND (
       (line.account BETWEEN '7000' AND '7199') -- Tax & Customs start
    OR (line.account BETWEEN '7200' AND '7799') -- Non-Tax
  )
  -- Still excluding the 76061 range as requested
  AND line.account NOT LIKE '76061%'

GROUP BY
    CASE
        WHEN hdr.business_unit LIKE 'E%' THEN 'APE'
        WHEN REGEXP_LIKE(hdr.business_unit, '^(CO|DS|PV|PT)') THEN 'Sub-national'
        WHEN NOT REGEXP_LIKE(hdr.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') THEN 'National'
        ELSE 'Unmapped'
    END
ORDER BY 
    CASE 
        WHEN gov_level = 'National' THEN 1 
        WHEN gov_level = 'Sub-national' THEN 2 
        WHEN gov_level = 'APE' THEN 3 
        ELSE 4 
    END;