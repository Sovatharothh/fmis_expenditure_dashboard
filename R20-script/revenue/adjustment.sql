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
 , SUM(line.monetary_amount)
 , 0
 , 0
 , 0
 , 0 
  FROM PS_KK_BUDGET_HDR hdr
  , PS_KK_BUDGET_LN line 
 WHERE hdr.BUSINESS_UNIT = line.BUSINESS_UNIT 
   AND hdr.JOURNAL_ID = line.JOURNAL_ID 
   AND (hdr.JOURNAL_DATE = line.JOURNAL_DATE) 
   AND hdr.UNPOST_SEQ = line.UNPOST_SEQ 
   AND hdr.ledger_group = %Bind(LEDGER_GROUP)   
   AND hdr.fiscal_year = %Bind(FISCAL_YEAR)   
   AND hdr.accounting_period BETWEEN 1 AND %Bind(PERIOD_TO)   
   AND hdr.unpost_seq = '0'   
   AND hdr.kk_budg_trans_type = '1'   
   AND hdr.bd_hdr_status = 'P'   
   AND ( 'N' = 'Y'   
   AND (%Bind(LEDGER_GROUP_TYPE) = 'E'   
   AND line.budget_ref IN ('GENERAL','PETYCASH','A_TYPE','B_TYPE','C_TYPE')   
    OR %Bind(LEDGER_GROUP_TYPE) <> 'E')   
    OR 'N' = 'N')   
   AND line.monetary_amount <> 0 
   AND EXISTS ( 
 SELECT 'x' 
  FROM ps_z_kk_budget_hdr z_hdr 
 WHERE z_hdr.business_unit = hdr.business_unit 
   AND z_hdr.journal_id = hdr.journal_id 
   AND z_hdr.journal_date = hdr.journal_date 
   AND z_hdr.unpost_seq = hdr.unpost_seq 
   AND z_hdr.z_badj_rsn_cd = ( 
 SELECT z_badj_rsn_cd 
  FROM ps_z_badj_rsn rsn 
 WHERE rsn.setid = ( 
 SELECT setid 
  FROM ps_set_cntrl_rec 
 WHERE setcntrlvalue = hdr.business_unit 
   AND recname = 'KK_BUDGET_TYPE') 
   AND rsn.z_dflt_flg = 'Y' 
   AND rsn.EFFDT=(
 SELECT MAX(EFFDT) 
  FROM PS_Z_BADJ_RSN rsn_ed 
 WHERE rsn_ed.SETID=rsn.SETID 
   AND rsn_ed.Z_BADJ_RSN_CD=rsn.Z_BADJ_RSN_CD 
   AND rsn_ed.EFFDT<=to_date(to_char(%Bind(FISCAL_YEAR) || '-01-01'), 'YYYY-MM-DD')))) 
  GROUP BY  line.business_unit, line.operating_unit, SUBSTR(line.account,1,2), SUBSTR(line.account,1,4), line.account, line.program_code, line.deptid, 
line.budget_ref, accounting_period
