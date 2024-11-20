/* Create a SAS dataset based on the LUL structure */
data lul_structure;
    infile datalines dlm=',' dsd;
    input Key : $20. LUL_RunID : $7. LUL_DateTime : datetime19.;
    format LUL_DateTime datetime19.;
datalines;
1234567,0006500,2023-05-13:12:30:00
;
run;

/* View the dataset */
proc print data=lul_structure;
run;
