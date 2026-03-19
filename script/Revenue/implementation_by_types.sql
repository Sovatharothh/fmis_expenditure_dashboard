-- implementation by types
SELECT
    CASE 
        -- 1. CUSTOMS (Specific sub-ranges from your image)
        WHEN (line.account BETWEEN '70025' AND '70027') 
          OR (line.account BETWEEN '70032' AND '70033')
          OR (line.account BETWEEN '7100' AND '71016') 
          THEN 'Customs'
        
        -- 2. TAX (General 70xxx range, minus the Customs sub-ranges)
        WHEN (line.account BETWEEN '7001' AND '70999') 
          THEN 'Tax'
        
        -- 3. NON-TAX (72xxx through 77xxx series)
        WHEN (line.account BETWEEN '7200' AND '77981') 
          THEN 'Non-Tax'
        
        ELSE 'Other Revenue/Adjustments'
    END AS revenue_category,
    
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
  
  -- Exclude the specific internal account that causes "too much amount"
  AND line.account NOT LIKE '76061%'

GROUP BY
    CASE 
        WHEN (line.account BETWEEN '70025' AND '70027') 
          OR (line.account BETWEEN '70032' AND '70033')
          OR (line.account BETWEEN '7100' AND '71016') THEN 'Customs'
        WHEN (line.account BETWEEN '7001' AND '70999') THEN 'Tax'
        WHEN (line.account BETWEEN '7200' AND '77981') THEN 'Non-Tax'
        ELSE 'Other Revenue/Adjustments'
    END

ORDER BY 
    CASE 
        WHEN revenue_category = 'Tax' THEN 1
        WHEN revenue_category = 'Non-Tax' THEN 2
        WHEN revenue_category = 'Customs' THEN 3
        ELSE 4
    END;





-- implementation by types and modified law
WITH modified_law_data AS (
    SELECT
        CASE
            WHEN (line.account BETWEEN '70025' AND '70027')
              OR (line.account BETWEEN '70032' AND '70033')
              OR (line.account BETWEEN '7100' AND '71016') THEN 'Customs'
            WHEN (line.account BETWEEN '7001' AND '70999') THEN 'Tax'
            WHEN (line.account BETWEEN '7200' AND '77981') THEN 'Non-Tax'
            ELSE 'Other Revenue'
        END AS revenue_category,
        -SUM(line.monetary_amount) AS modified_law
    FROM ps_kk_budget_hdr hdr
    JOIN ps_kk_budget_ln line
      ON line.business_unit = hdr.business_unit
     AND line.journal_id    = hdr.journal_id
     AND line.journal_date  = hdr.journal_date
     AND line.unpost_seq    = hdr.unpost_seq
    WHERE hdr.ledger_group = 'CCRVGROUP'
      AND hdr.fiscal_year = 2026
        and ( REGEXP_LIKE(hdr.business_unit, '^(CO|DS|PV|PT)') or
        NOT REGEXP_LIKE(hdr.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') )
      AND hdr.unpost_seq = 0
      AND line.account NOT LIKE '76061%'
      AND (
            hdr.bd_hdr_status = 'P'
            OR (
                hdr.bd_hdr_status <> 'P'
                AND EXISTS (
                    SELECT 1 FROM ps_kk_budget_hdr h2
                    WHERE h2.business_unit = hdr.business_unit
                      AND h2.journal_id    = hdr.journal_id
                      AND h2.unpost_seq    = 1
                )
            )
          )
    GROUP BY
        CASE
            WHEN (line.account BETWEEN '70025' AND '70027')
              OR (line.account BETWEEN '70032' AND '70033')
              OR (line.account BETWEEN '7100' AND '71016') THEN 'Customs'
            WHEN (line.account BETWEEN '7001' AND '70999') THEN 'Tax'
            WHEN (line.account BETWEEN '7200' AND '77981') THEN 'Non-Tax'
            ELSE 'Other Revenue'
        END
),

implementation_data AS (
    SELECT
        CASE
            WHEN (line.account BETWEEN '70025' AND '70027')
              OR (line.account BETWEEN '70032' AND '70033')
              OR (line.account BETWEEN '7100' AND '71016') THEN 'Customs'
            WHEN (line.account BETWEEN '7001' AND '70999') THEN 'Tax'
            WHEN (line.account BETWEEN '7200' AND '77981') THEN 'Non-Tax'
            ELSE 'Other Revenue'
        END AS revenue_category,
        SUM(line.monetary_amount) * -1 AS implementation
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
      AND hdr.jrnl_hdr_status = 'P'
      AND line.jrnl_line_source <> 'CLO'
      AND line.account NOT LIKE '76061%'
    GROUP BY
        CASE
            WHEN (line.account BETWEEN '70025' AND '70027')
              OR (line.account BETWEEN '70032' AND '70033')
              OR (line.account BETWEEN '7100' AND '71016') THEN 'Customs'
            WHEN (line.account BETWEEN '7001' AND '70999') THEN 'Tax'
            WHEN (line.account BETWEEN '7200' AND '77981') THEN 'Non-Tax'
            ELSE 'Other Revenue'
        END
)

SELECT
    COALESCE(i.revenue_category, m.revenue_category) AS revenue_category,
    NVL(i.implementation, 0) AS implementation,
    NVL(m.modified_law, 0) AS modified_law
FROM implementation_data i
FULL OUTER JOIN modified_law_data m 
    ON i.revenue_category = m.revenue_category
ORDER BY
    CASE 
        WHEN revenue_category = 'Tax' THEN 1
        WHEN revenue_category = 'Non-Tax' THEN 2
        WHEN revenue_category = 'Customs' THEN 3
        ELSE 4
    END;