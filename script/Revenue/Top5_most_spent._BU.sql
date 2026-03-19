SELECT * FROM (
    SELECT
        hdr.business_unit,
        SUM(line.monetary_amount) * -1 AS total_implementation
    FROM PS_JRNL_HEADER hdr
    JOIN PS_JRNL_LN line
      ON hdr.business_unit = line.business_unit
     AND hdr.journal_id    = line.journal_id
     AND hdr.journal_date  = line.journal_date
     AND hdr.unpost_seq    = line.unpost_seq
    WHERE hdr.unpost_seq = 0
      AND hdr.fiscal_year = 2025
      AND hdr.jrnl_hdr_status = 'P'
      AND line.jrnl_line_source <> 'CLO'
      -- Only National units: Exclude the following prefixes
      AND NOT REGEXP_LIKE(hdr.business_unit, '^(PT|NT|FMIS|CMB|CO|PV|DS|E|LD)')
      -- Revenue filter based on your image ranges
      AND (
           (line.account BETWEEN '7001' AND '7199') 
        OR (line.account BETWEEN '7200' AND '77981')
      )
      -- Specific exclusion
      AND line.account NOT LIKE '76061%'
    GROUP BY
        hdr.business_unit
    ORDER BY total_implementation DESC
)
WHERE ROWNUM <= 5;