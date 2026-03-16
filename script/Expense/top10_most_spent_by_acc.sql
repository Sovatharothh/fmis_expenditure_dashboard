SELECT *
FROM (
    SELECT
        a.account,
        SUM(a.monetary_amount) AS implementation
    FROM PS_Z_Q03_QRY_VW a
    WHERE a.accounting_dt >= DATE '2025-01-01'
      AND a.accounting_dt <= DATE '2025-12-31'
      AND a.budget_ref LIKE '2025%'
      AND a.budget_ref NOT LIKE 'SD%'
      AND a.post_status_ap = 'P'
      AND a.gl_distrib_status = 'D'
      AND (a.account LIKE '2%' OR a.account LIKE '6%' OR a.account = '70091')

    GROUP BY a.account
    ORDER BY implementation DESC
)
WHERE ROWNUM <= 10;


-- select on the first 2 digits
SELECT *
FROM (
    SELECT
        SUBSTR(a.account, 1, 2) AS account_prefix,
        SUM(a.monetary_amount) AS implementation
    FROM PS_Z_Q03_QRY_VW a
    WHERE a.accounting_dt >= DATE '2025-01-01'
      AND a.accounting_dt <= DATE '2025-12-31'
      AND a.budget_ref LIKE '2025%'
      AND a.budget_ref NOT LIKE 'SD%'
      AND a.post_status_ap = 'P'
      AND a.gl_distrib_status = 'D'
      AND (a.account LIKE '2%' OR a.account LIKE '6%' OR a.account = '70091')
    GROUP BY SUBSTR(a.account, 1, 2)
    ORDER BY implementation DESC
)
WHERE ROWNUM <= 10;


-- modified law vs implementation
WITH modified_law_data AS (
    SELECT
        CASE
            WHEN SUBSTR(line.account, 1, 2) = '60' THEN 'Staff Charges'
            WHEN SUBSTR(line.account, 1, 2) = '61' THEN 'Operating Expenditures'
            WHEN SUBSTR(line.account, 1, 2) = '21' THEN 'Investment Expenditure'
            WHEN SUBSTR(line.account, 1, 2) = '66' THEN 'Financial Charges'
            WHEN SUBSTR(line.account, 1, 2) IN ('62', '65') THEN 'Transfer Expenditure'
            WHEN SUBSTR(line.account, 1, 2) = '63' THEN 'Other Expenditure'
        END AS expenditure_category,

        -SUM(line.monetary_amount) AS modified_law
    FROM ps_kk_budget_hdr hdr
    JOIN ps_kk_budget_ln line
      ON line.business_unit = hdr.business_unit
     AND line.journal_id    = hdr.journal_id
     AND line.journal_date  = hdr.journal_date
     AND line.unpost_seq    = hdr.unpost_seq
    WHERE hdr.ledger_group = 'CCEXGROUP'
      AND hdr.fiscal_year = 2025
      AND hdr.unpost_seq = 0
      AND line.budget_ref <> 'SUBSIDY'
      AND SUBSTR(line.account, 1, 2) IN ('21','60','61','62','63','65','66')
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
            WHEN SUBSTR(line.account, 1, 2) = '60' THEN 'Staff Charges'
            WHEN SUBSTR(line.account, 1, 2) = '61' THEN 'Operating Expenditures'
            WHEN SUBSTR(line.account, 1, 2) = '21' THEN 'Investment Expenditure'
            WHEN SUBSTR(line.account, 1, 2) = '66' THEN 'Financial Charges'
            WHEN SUBSTR(line.account, 1, 2) IN ('62', '65') THEN 'Transfer Expenditure'
            WHEN SUBSTR(line.account, 1, 2) = '63' THEN 'Other Expenditure'
        END
),

implementation_data AS (
    SELECT
        CASE
            WHEN SUBSTR(a.account, 1, 2) = '60' THEN 'Staff Charges'
            WHEN SUBSTR(a.account, 1, 2) = '61' THEN 'Operating Expenditures'
            WHEN SUBSTR(a.account, 1, 2) = '21' THEN 'Investment Expenditure'
            WHEN SUBSTR(a.account, 1, 2) = '66' THEN 'Financial Charges'
            WHEN SUBSTR(a.account, 1, 2) IN ('62', '65') THEN 'Transfer Expenditure'
            WHEN SUBSTR(a.account, 1, 2) = '63' THEN 'Other Expenditure'
        END AS expenditure_category,

        SUM(a.monetary_amount) AS implementation
    FROM PS_Z_Q03_QRY_VW a
    WHERE a.accounting_dt BETWEEN DATE '2025-01-01' AND DATE '2025-12-31'
      AND a.budget_ref LIKE '2025%'
      AND a.budget_ref NOT LIKE 'SD%'
      AND a.post_status_ap = 'P'
      AND a.gl_distrib_status = 'D'
      AND SUBSTR(a.account, 1, 2) IN ('21','60','61','62','63','65','66')
    GROUP BY
        CASE
            WHEN SUBSTR(a.account, 1, 2) = '64' THEN 'Staff Charges'
            WHEN SUBSTR(a.account, 1, 2) IN ('60', '61') THEN 'Operating Expenditures'
            WHEN SUBSTR(a.account, 1, 1) = '2' THEN 'Investment Expenditure'
            WHEN SUBSTR(a.account, 1, 2) = '66' THEN 'Financial Charges'
            WHEN SUBSTR(a.account, 1, 2) IN ('62', '65') THEN 'Transfer Expenditure'
            WHEN (SUBSTR(a.account, 1, 2) IN ('63', '67', '68', '69') or a.account like '7009%') THEN 'Other Expenditure'
        END
)

SELECT
    COALESCE(m.expenditure_category, i.expenditure_category) AS expenditure_category,
    NVL(i.implementation, 0) AS implementation,
    NVL(m.modified_law, 0) AS modified_law
FROM modified_law_data m
FULL OUTER JOIN implementation_data i
    ON m.expenditure_category = i.expenditure_category
ORDER BY
    CASE COALESCE(m.expenditure_category, i.expenditure_category)
        WHEN 'Staff Charges' THEN 1
        WHEN 'Operating Expenditures' THEN 2
        WHEN 'Investment Expenditure' THEN 3
        WHEN 'Financial Charges' THEN 4
        WHEN 'Transfer Expenditure' THEN 5
        WHEN 'Other Expenditure' THEN 6
    END;