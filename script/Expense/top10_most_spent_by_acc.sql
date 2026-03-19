-- modified law vs implementation
WITH modified_law_data AS (
    SELECT
        CASE
            WHEN SUBSTR(line.account, 1, 2) = '64' THEN 'Staff Charges'
            WHEN SUBSTR(line.account, 1, 2) IN ('60', '61') THEN 'Operating Expenditures'
            WHEN SUBSTR(line.account, 1, 1) = '2' THEN 'Investment Expenditure'
            WHEN SUBSTR(line.account, 1, 2) = '66' THEN 'Financial Charges'
            WHEN SUBSTR(line.account, 1, 2) IN ('62', '65') THEN 'Transfer Expenditure'
            WHEN (SUBSTR(line.account, 1, 2) IN ('63', '67', '68', '69') OR line.account LIKE '7009%') THEN 'Other Expenditure'
        END AS expenditure_category,
        -SUM(line.monetary_amount) AS modified_law
    FROM ps_kk_budget_hdr hdr
    JOIN ps_kk_budget_ln line
      ON line.business_unit = hdr.business_unit
     AND line.journal_id    = hdr.journal_id
     AND line.journal_date  = hdr.journal_date
     AND line.unpost_seq    = hdr.unpost_seq
    WHERE hdr.ledger_group = 'CCEXGROUP'
      AND hdr.fiscal_year = 2026
  and ( REGEXP_LIKE(hdr.business_unit, '^(CO|DS|PV|PT)') or
        NOT REGEXP_LIKE(hdr.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') )
      AND hdr.unpost_seq = 0
      AND line.budget_ref <> 'SUBSIDY'
      -- Updated filter to match your CASE logic (all 2s, 6s, and 7009)
      AND (SUBSTR(line.account, 1, 1) = '2' 
           OR SUBSTR(line.account, 1, 1) = '6' 
           OR line.account LIKE '7009%')
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
            WHEN SUBSTR(line.account, 1, 2) = '64' THEN 'Staff Charges'
            WHEN SUBSTR(line.account, 1, 2) IN ('60', '61') THEN 'Operating Expenditures'
            WHEN SUBSTR(line.account, 1, 1) = '2' THEN 'Investment Expenditure'
            WHEN SUBSTR(line.account, 1, 2) = '66' THEN 'Financial Charges'
            WHEN SUBSTR(line.account, 1, 2) IN ('62', '65') THEN 'Transfer Expenditure'
            WHEN (SUBSTR(line.account, 1, 2) IN ('63', '67', '68', '69') OR line.account LIKE '7009%') THEN 'Other Expenditure'
        END
),

implementation_data AS (
    SELECT
        CASE
            WHEN SUBSTR(a.account, 1, 2) = '64' THEN 'Staff Charges'
            WHEN SUBSTR(a.account, 1, 2) IN ('60', '61') THEN 'Operating Expenditures'
            WHEN SUBSTR(a.account, 1, 1) = '2' THEN 'Investment Expenditure'
            WHEN SUBSTR(a.account, 1, 2) = '66' THEN 'Financial Charges'
            WHEN SUBSTR(a.account, 1, 2) IN ('62', '65') THEN 'Transfer Expenditure'
            WHEN (SUBSTR(a.account, 1, 2) IN ('63', '67', '68', '69') OR a.account LIKE '7009%') THEN 'Other Expenditure'
        END AS expenditure_category,
        SUM(a.monetary_amount) AS implementation
    FROM PS_Z_Q03_QRY_VW a
    WHERE a.accounting_dt BETWEEN DATE '2026-01-01' AND DATE '2026-12-31'
  and ( REGEXP_LIKE(a.business_unit, '^(CO|DS|PV|PT)') or
        NOT REGEXP_LIKE(a.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') )
      AND a.budget_ref LIKE '%2026%'
      AND a.budget_ref NOT LIKE 'SD%'
      AND a.post_status_ap = 'P'
      AND a.gl_distrib_status = 'D'
      -- Updated filter to match your CASE logic
      AND (SUBSTR(a.account, 1, 1) = '2' 
           OR SUBSTR(a.account, 1, 1) = '6' 
           OR a.account LIKE '7009%')
    GROUP BY
        CASE
            WHEN SUBSTR(a.account, 1, 2) = '64' THEN 'Staff Charges'
            WHEN SUBSTR(a.account, 1, 2) IN ('60', '61') THEN 'Operating Expenditures'
            WHEN SUBSTR(a.account, 1, 1) = '2' THEN 'Investment Expenditure'
            WHEN SUBSTR(a.account, 1, 2) = '66' THEN 'Financial Charges'
            WHEN SUBSTR(a.account, 1, 2) IN ('62', '65') THEN 'Transfer Expenditure'
            WHEN (SUBSTR(a.account, 1, 2) IN ('63', '67', '68', '69') OR a.account LIKE '7009%') THEN 'Other Expenditure'
        END
)


SELECT
    COALESCE(m.expenditure_category, i.expenditure_category) AS expenditure_category,
    NVL(i.implementation, 0) AS implementation,
    NVL(m.modified_law, 0) AS modified_law
FROM modified_law_data m
FULL OUTER JOIN implementation_data i
    ON m.expenditure_category = i.expenditure_category
WHERE COALESCE(m.expenditure_category, i.expenditure_category) IS NOT NULL
ORDER BY
    CASE COALESCE(m.expenditure_category, i.expenditure_category)
        WHEN 'Staff Charges' THEN 1
        WHEN 'Operating Expenditures' THEN 2
        WHEN 'Investment Expenditure' THEN 3
        WHEN 'Financial Charges' THEN 4
        WHEN 'Transfer Expenditure' THEN 5
        WHEN 'Other Expenditure' THEN 6
    END;