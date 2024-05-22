
 meor_columns = ['Order Event', 'Fix_Col_0', 'FirmROID', 'MsgType', 'CAT_IM_ID', 'Date', 'Order ID',
                            'Symbol',
                            'Fix_Col_1', 'TimeStamp', 'Fix_Col_2', 'Fix_Col_3', 'Fix_Col_4', 'Fix_Col_5', 'SideType',
                            'Price',
                            'Quantity', 'Fix_Col_6', 'OrderType', 'TIF', 'Trading_Session', 'FDID', 'Fix_Col_7',
                            'Fix_Col_8',
                            'Fix_Col_9', 'Fix_Col_10', 'Fix_Col_11', 'Fix_Col_12', 'Fix_Col_13', 'Fix_Col_14',
                            'Fix_Col_15',
                            'Fix_Col_16']

            meno_columns = ['Order Event', 'Fix_Col_0', 'FirmROID', 'MsgType', 'CAT_IM_ID',
                       'Date', 'Order ID', 'Symbol', 'TimeStamp', 'Fix_Col_1', 'Fix_Col_2', 'Fix_Col_3', 'Fix_Col_4',
                       'Fix_Col_5', 'Fix_Col_6', 'Fix_Col_7', 'Fix_Col_8', 'SideType', 'Price', 'Quantity', 'Fix_Col_9',
                       'OrderType', 'TIF', 'Trading_Session', 'Fix_Col_10', 'Fix_Col_11', 'FDID', 'Acc Type',
                       'Fix_Col_12',
                       'Fix_Col_13', 'Fix_Col_14', 'Fix_Col_15', 'Fix_Col_16', 'Fix_Col_17', 'Fix_Col_18', 'Fix_Col_19',
                       'Fix_Col_20', 'Fix_Col_21', 'Fix_Col_22', 'Fix_Col_23', 'Fix_Col_24', 'Fix_Col_25', 'Fix_Col_26',
                       'Fix_Col_27', 'Fix_Col_28', 'Fix_Col_29']

the Result i'm getting 
MENO_RESULT = NEW,,20240513_CAT-VCVW-1,MENO,VCVW,20240513T000000.00000000,CAT-VCVW-OrderID-1,REGCO,20240513T160000.517000000,False,False,,,,T,False,,B,,100.0,,MKT,GTX=20240513,ALL,,False,4540540244050736652713500211690321808548,A,False,,,False,N,,,,,,,,,,,,,
MEOR_RESULT = NEW,,20240513_CAT-VCVW-74,MEOR,VCVW,20240513T000000.00000000,CAT-VCVW-OrderID-33,PNFPP,,20240513T160001.346000000,False,False,,126588:VCVW,7897:INCA,F,VCTY-TAK2-258998,,B,23.28,100,,LMT,GTX=20240513,ALL,False,NA,,False,False,,False,,,,,,,,,,,,,,


the result I want 
MENO_RESULT = NEW,,20240513_CAT-VCVW-1,MENO,VCVW,20240513T000000.00000000,CAT-VCVW-OrderID-1,REGCO,20240513T160000.517000000,False,False,,,,T,False,,B,,100.0,,MKT,GTX=20240513,ALL,,False,4540540244050736652713500211690321808548,A,False,,,False,N,,,,,,,,,,,,,
MEOR_RESULT = NEW,,20240513_CAT-VCVW-74,MEOR,VCVW,20240513T000000.00000000,CAT-VCVW-OrderID-33,PNFPP,,20240513T160001.346000000,False,False,,126588:VCVW,7897:INCA,F,VCTY-TAK2-258998,,B,23.28,100,,LMT,GTX=20240513,ALL,False,NA,,False,False,,False,,,,

result = pd.concat([result_MENO, result_MEOR])
        
