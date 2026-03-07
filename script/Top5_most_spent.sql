SELECT *
FROM (
    SELECT
        a.business_unit,
        SUM(a.monetary_amount) AS implementation
    FROM PS_Z_Q03_QRY_VW a
    WHERE a.accounting_dt >= DATE '2025-01-01'
      AND a.accounting_dt <= DATE '2025-12-31'
      AND a.budget_ref LIKE '2025%'
      AND a.budget_ref NOT LIKE 'SD%'
      AND a.post_status_ap = 'P'
      AND a.gl_distrib_status = 'D'
      AND (a.account LIKE '2%' OR a.account LIKE '6%' OR a.account = '70091')

    GROUP BY a.business_unit
    ORDER BY implementation DESC
)
WHERE ROWNUM <= 5;