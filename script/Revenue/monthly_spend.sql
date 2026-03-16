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
    END AS month_name,
    SUM(line.monetary_amount) * -1 AS implementation
FROM PS_JRNL_HEADER hdr,
     PS_JRNL_LN line
WHERE hdr.business_unit = line.business_unit
  AND hdr.journal_id    = line.journal_id
  AND hdr.journal_date  = line.journal_date
  AND hdr.unpost_seq    = line.unpost_seq
  AND hdr.unpost_seq = 0
  AND hdr.fiscal_year = 2026
  AND hdr.accounting_period BETWEEN 1 AND 12
  AND hdr.jrnl_hdr_status = 'P'
  AND line.jrnl_line_source <> 'CLO'
  AND (line.account LIKE '7%' OR line.account not LIKE '76061%')
GROUP BY hdr.accounting_period
ORDER BY hdr.accounting_period;