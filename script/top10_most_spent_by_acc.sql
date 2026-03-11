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