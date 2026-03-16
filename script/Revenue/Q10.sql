SELECT
    CASE
        WHEN a.business_unit LIKE 'E%' THEN 'APE'
        WHEN REGEXP_LIKE(a.business_unit, '^(CO|DS|PV|PT)') THEN 'Sub-national'
        WHEN NOT REGEXP_LIKE(a.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') THEN 'National'
    END AS gov_level,

    -SUM(CASE 
            WHEN hdr.kk_budg_trans_type = '0'
            THEN line.monetary_amount 
            ELSE 0 
        END) AS original_budget,

    -SUM(CASE 
            WHEN hdr.kk_budg_trans_type = '1'
            THEN line.monetary_amount 
            ELSE 0 
        END) AS adjustment_budget,

    -SUM(CASE 
            WHEN hdr.kk_budg_trans_type NOT IN ('0','1')
            THEN line.monetary_amount 
            ELSE 0 
        END) AS transfer_budget,

    -SUM(line.monetary_amount) AS current_budget

FROM ps_kk_budget_hdr hdr
JOIN ps_kk_budget_ln line
  ON line.business_unit = hdr.business_unit
 AND line.journal_id    = hdr.journal_id
 AND line.journal_date  = hdr.journal_date
 AND line.unpost_seq    = hdr.unpost_seq

WHERE hdr.ledger_group = 'CCRVGROUP'
  AND hdr.fiscal_year = 2025
  AND hdr.unpost_seq = 0
  AND (
        hdr.bd_hdr_status = 'P'
        OR (
            hdr.bd_hdr_status <> 'P'
            AND EXISTS (
                SELECT 1
                FROM ps_kk_budget_hdr h2
                WHERE h2.business_unit = hdr.business_unit
                  AND h2.journal_id    = hdr.journal_id
                  AND h2.journal_date  = hdr.journal_date
                  AND h2.unpost_seq    = 1
                  AND h2.bd_hdr_status <> 'P'
            )
        )
      )

GROUP BY
    CASE
        WHEN a.business_unit LIKE 'E%' THEN 'APE'
        WHEN REGEXP_LIKE(a.business_unit, '^(CO|DS|PV|PT)') THEN 'Sub-national'
        WHEN NOT REGEXP_LIKE(a.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') THEN 'National'
    END AS gov_level,

ORDER BY gov_level;