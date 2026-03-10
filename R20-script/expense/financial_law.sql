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
 , BUSINESS_UNIT
 , OPERATING_UNIT
 , SUBSTR(led.account
 ,1
 ,2)
 , SUBSTR(led.account
 ,1
 ,4)
 , ACCOUNT
 , PROGRAM_CODE
 , DEPTID
 , BUDGET_REF
 , 1
 , SUM(led.posted_total_amt) * -1
 , 0
 , 0
 , 0
 , 0
 , 0
 , 0
 , 0 
  FROM PS_LEDGER_KK led 
  , PS_LED_GRP_LED_TBL lgrp 
  , PS_SET_CNTRL_REC setid 
 WHERE setid.setcntrlvalue = led.business_unit 
   AND setid.recname = 'LED_GRP_LED_TBL' 
   AND lgrp.setid = setid.setid 
   AND lgrp.ledger_group = %Bind(LEDGER_GROUP) 
   AND lgrp.ledger_type_kk = '0' 
   AND led.ledger = lgrp.ledger 
   AND led.kk_budg_trans_type = '0' 
   AND led.fiscal_year = %Bind(FISCAL_YEAR) 
   AND ( ( SUBSTR(led.account,1,1) NOT IN ('2','5','6') 
   AND led.budget_ref = 'GENERAL' ) 
    OR SUBSTR(led.account,1,1) IN ('2','5','6') 
   AND led.budget_ref IN ('GENERAL', 'A_TYPE', 'A1_TYPE', 'B_TYPE', 'C_TYPE') ) 
  GROUP BY  led.business_unit, led.operating_unit, SUBSTR(led.account,1,2), SUBSTR(led.account,1,4), led.account, led.program_code, led.deptid, led.budget_ref
