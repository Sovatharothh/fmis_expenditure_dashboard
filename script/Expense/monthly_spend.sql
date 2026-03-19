-- from Q03: exclude 66981
SELECT
    TO_CHAR(a.accounting_dt, 'Mon') AS month_name,
    SUM(a.monetary_amount) AS implementation
FROM PS_Z_Q03_QRY_VW a
WHERE a.accounting_dt >= DATE '2025-01-01'
  AND a.accounting_dt <= DATE '2025-12-31'
  AND a.budget_ref LIKE '2025%'
  AND a.budget_ref NOT LIKE 'SD%'
  AND a.post_status_ap = 'P'
  AND a.gl_distrib_status = 'D'
  AND (a.account LIKE '2%' OR a.account LIKE '6%' OR a.account = '70091')
GROUP BY TO_CHAR(a.accounting_dt, 'Mon'), TO_CHAR(a.accounting_dt, 'MM')
ORDER BY TO_CHAR(a.accounting_dt, 'MM');


-- from R20: exclude 66981
SELECT
    CASE hdr.accounting_period
        WHEN 1 THEN 'Jan'
        WHEN 2 THEN 'Feb'
        WHEN 3 THEN 'Mar'
        WHEN 4 THEN 'Apr'
        WHEN 5 THEN 'May'
        WHEN 6 THEN 'Jun'
        WHEN 7 THEN 'Jul'
        WHEN 8 THEN 'Aug'
        WHEN 9 THEN 'Sep'
        WHEN 10 THEN 'Oct'
        WHEN 11 THEN 'Nov'
        WHEN 12 THEN 'Dec'
    END AS month,
    SUM(line.monetary_amount) AS implementation
FROM PS_JRNL_HEADER hdr
JOIN PS_JRNL_LN line
  ON hdr.business_unit = line.business_unit
 AND hdr.journal_id = line.journal_id
 AND hdr.journal_date = line.journal_date
 AND hdr.unpost_seq = line.unpost_seq
WHERE hdr.unpost_seq = 0
  AND hdr.fiscal_year = 2026
    and ( REGEXP_LIKE(hdr.business_unit, '^(CO|DS|PV|PT)') or
        NOT REGEXP_LIKE(hdr.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E)') )
  AND hdr.accounting_period BETWEEN 1 AND 12
  AND hdr.jrnl_hdr_status = 'P'
  AND line.jrnl_line_source <> 'CLO'
  AND (
        (SUBSTR(line.account, 1, 2) IN ('27', '50')
         AND line.jrnl_line_source NOT IN ('GAR', 'PNL', 'SCP'))
        OR SUBSTR(line.account, 1, 2) NOT IN ('27', '50')
      )
  AND hdr.journal_id NOT IN ('0002249795', '0002251264')
  AND (
        line.account LIKE '2%'
        OR line.account LIKE '6%'
        OR line.account LIKE '7009%'
      )
  and line.account not like '66981'
GROUP BY hdr.accounting_period
ORDER BY hdr.accounting_period;