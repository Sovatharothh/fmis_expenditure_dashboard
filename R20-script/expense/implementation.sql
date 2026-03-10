
SELECT line.business_unit,
       OPERATING_UNIT,
       SUBSTR(line.account, 1, 2),
       SUBSTR(line.account, 1, 4),
       ACCOUNT,
       PROGRAM_CODE,
       DEPTID,
       BUDGET_REF,
       ACCOUNTING_PERIOD,
       0,
       0,
       0,
       0,
       0,
       0,
       SUM(line.monetary_amount),
       0
  FROM PS_JRNL_HEADER hdr, PS_JRNL_LN line
 WHERE hdr.BUSINESS_UNIT = line.BUSINESS_UNIT
   AND hdr.JOURNAL_ID = line.JOURNAL_ID
   AND (hdr.JOURNAL_DATE = line.JOURNAL_DATE)
   AND hdr.UNPOST_SEQ = line.UNPOST_SEQ
   AND hdr.unpost_seq = 0
   AND hdr.fiscal_year = 2026
   AND hdr.accounting_period BETWEEN 1 AND 12
   AND hdr.jrnl_hdr_status = 'P'
   AND line.jrnl_line_source <> 'CLO'
   AND ((SUBSTR(line.account, 1, 2) IN ('27', '50') AND
       line.jrnl_line_source NOT IN ('GAR', 'PNL', 'SCP')) OR
       SUBSTR(line.account, 1, 2) NOT IN ('27', '50'))
   AND hdr.journal_id NOT IN ('0002249795', '0002251264')
 GROUP BY line.business_unit,
          line.operating_unit,
          SUBSTR(line.account, 1, 2),
          SUBSTR(line.account, 1, 4),
          line.account,
          line.program_code,
          line.deptid,
          line.budget_ref,
          accounting_period
