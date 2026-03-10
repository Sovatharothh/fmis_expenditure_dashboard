INSERT INTO PS_Z_RPT_R20_T1 (PROCESS_INSTANCE
 , BUSINESS_UNIT
 , OPERATING_UNIT
 , CHAPTER
 , Z_ACCOUNT
 , ACCOUNT
 , PROGRAM_CODE
 , DEPTID
 , BUDGET_REF
 , ACCOUNTING_PERIOD
 , AMOUNT_1
 , AMOUNT_2
 , AMOUNT_3
 , AMOUNT_4
 , Z_AMOUNT_5
 , Z_AMOUNT_6
 , Z_AMOUNT_7
 , Z_AMOUNT_8) 
 SELECT %Bind(PROCESS_INSTANCE)
 , line.business_unit
 , OPERATING_UNIT
 , SUBSTR(line.account
 ,1
 ,2)
 , SUBSTR(line.account
 ,1
 ,4)
 , ACCOUNT
 , PROGRAM_CODE
 , DEPTID
 , BUDGET_REF
 , ACCOUNTING_PERIOD
 , 0
 , 0
 , 0
 , 0
 , 0
 , 0
 , SUM(line.monetary_amount) * -1
 , 0 
  FROM PS_JRNL_HEADER hdr
  , PS_JRNL_LN line 
 WHERE hdr.BUSINESS_UNIT = line.BUSINESS_UNIT 
   AND hdr.JOURNAL_ID = line.JOURNAL_ID 
   AND (hdr.JOURNAL_DATE = line.JOURNAL_DATE) 
   AND hdr.UNPOST_SEQ = line.UNPOST_SEQ 
   AND hdr.unpost_seq = 0 
   AND hdr.fiscal_year = %Bind(FISCAL_YEAR) 
   AND hdr.accounting_period BETWEEN %Bind(PERIOD_FROM) AND %Bind(PERIOD_TO) 
   AND hdr.jrnl_hdr_status = 'P' 
   AND line.jrnl_line_source <> 'CLO' 
  GROUP BY  line.business_unit, line.operating_unit, SUBSTR(line.account,1,2), SUBSTR(line.account,1,4), line.account, line.program_code, line.deptid, 
line.budget_ref, accounting_period
