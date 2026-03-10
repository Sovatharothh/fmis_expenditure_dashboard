
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
       SUM(line.monetary_amount),
       0,
       0,
       0,
       0,
       0,
       0
  FROM PS_KK_BUDGET_HDR hdr, PS_KK_BUDGET_LN line
 WHERE hdr.BUSINESS_UNIT = line.BUSINESS_UNIT
   AND hdr.JOURNAL_ID = line.JOURNAL_ID
   AND (hdr.JOURNAL_DATE = line.JOURNAL_DATE)
   AND hdr.UNPOST_SEQ = line.UNPOST_SEQ
   AND hdr.ledger_group = 'CCRVGROUP'
   AND hdr.fiscal_year = 2026
   AND hdr.accounting_period BETWEEN 1 AND 12
   AND hdr.unpost_seq = '0'
   AND hdr.kk_budg_trans_type = '2'
   AND hdr.bd_hdr_status = 'P'
   AND ('N' = 'Y' AND (%Bind(LEDGER_GROUP_TYPE) = 'E' AND
       line.budget_ref IN
       ('GENERAL', 'PETYCASH', 'A_TYPE', 'B_TYPE', 'C_TYPE') OR
       %Bind(LEDGER_GROUP_TYPE) <> 'E') OR 'N' = 'N')
   AND line.monetary_amount > 0
   AND NOT EXISTS
 (SELECT 'x'
          FROM ps_kk_budget_ln line_ref2
         WHERE line_ref2.business_unit = line.business_unit
           AND line_ref2.journal_id = line.journal_id
           AND line_ref2.journal_date = line.journal_date
           AND line_ref2.unpost_seq = line.unpost_seq
           AND substr(line_ref2.account, 1, 2) = '69')
 GROUP BY line.business_unit,
          line.operating_unit,
          SUBSTR(line.account, 1, 2),
          SUBSTR(line.account, 1, 4),
          line.account,
          line.program_code,
          line.deptid,
          line.budget_ref,
          accounting_period
