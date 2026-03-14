-- implementation by sector and business unit
SELECT sector,
       business_unit,
       SUM(monetary_amount) AS implementation
FROM (
    SELECT
        a.business_unit,
        a.monetary_amount,
        CASE
            WHEN a.business_unit IN (
                '01000','02000','03000','04000','51000','54000',
                '08000','09000','10000','14000','28000','30000',
                '31000','33000','34000'
            ) THEN 'General Administration Sector'

            WHEN a.business_unit IN ('06000','71000','72000','26000')
            THEN 'National Defense and Security Sector'

            WHEN a.business_unit IN (
                '11000','12000','16000','18000','19000',
                '21000','23000','24000','32000'
            ) THEN 'Social Sector'

            WHEN a.business_unit IN (
                '53000','13000','15000','17000','20000',
                '22000','25000','27000','29000','35000'
            ) THEN 'Economic Sector'
        END AS sector
    FROM PS_Z_Q03_QRY_VW a
    WHERE a.accounting_dt >= DATE '2025-01-01'
      AND a.accounting_dt <= DATE '2025-12-31'
      AND a.budget_ref LIKE '%2025%'
      AND a.budget_ref NOT LIKE 'SD%'
      AND a.post_status_ap = 'P'
      AND a.gl_distrib_status = 'D'
      AND (
            a.account LIKE '2%'
            OR a.account LIKE '6%'
            OR a.account = '70091'
          )
) x
GROUP BY sector, business_unit
ORDER BY sector, business_unit;


-- implementation by sector
SELECT
    CASE
        WHEN a.business_unit IN (
            '01000','02000','03000','04000','51000',
            '54000','08000','09000','10000','14000',
            '28000','30000','31000','33000','34000'
        ) THEN 'General Administration Sector'

        WHEN a.business_unit IN (
            '06000','71000','72000','26000'
        ) THEN 'National Defense and Security Sector'

        WHEN a.business_unit IN (
            '11000','12000','16000','18000','19000',
            '21000','23000','24000','32000'
        ) THEN 'Social Sector'

        WHEN a.business_unit IN (
            '53000','13000','15000','17000','20000',
            '22000','25000','27000','29000','35000'
        ) THEN 'Economic Sector'
    END AS sector,
    
    SUM(a.monetary_amount) AS implementation

FROM PS_Z_Q03_QRY_VW a

WHERE a.accounting_dt >= DATE '2025-01-01'
  AND a.accounting_dt <= DATE '2025-12-31'
  AND a.budget_ref LIKE '2025%'
  AND a.budget_ref NOT LIKE 'SD%'
  AND a.post_status_ap = 'P'
  AND a.gl_distrib_status = 'D'
  AND (
        a.account LIKE '2%'
        OR a.account LIKE '6%'
        OR a.account = '70091'
      )

GROUP BY
    CASE
        WHEN a.business_unit IN (
            '01000','02000','03000','04000','51000',
            '54000','08000','09000','10000','14000',
            '28000','30000','31000','33000','34000'
        ) THEN 'General Administration Sector'

        WHEN a.business_unit IN (
            '06000','71000','72000','26000'
        ) THEN 'National Defense and Security Sector'

        WHEN a.business_unit IN (
            '11000','12000','16000','18000','19000',
            '21000','23000','24000','32000'
        ) THEN 'Social Sector'

        WHEN a.business_unit IN (
            '53000','13000','15000','17000','20000',
            '22000','25000','27000','29000','35000'
        ) THEN 'Economic Sector'
    END

ORDER BY sector;