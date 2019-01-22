##Author: Joseph  Rigdon

##Load packages and code
source('/Users/jrigdon/Box sync/Rigdon/Useful Functions/Tables.R')
library(survival)
source("/Users/jrigdon/Box sync/TG-HDL Chart Review/Statistical_Analysis/Survival/Code/kmplot.R")


##Function to get CI info
getCR = function(mod, name) {
mat = summary(mod)$coeff
tt = cbind(round(mat[, 2], 2), round(exp(confint(mod)), 2), mat[, 5])
a = which(rownames(tt)=="CHDsubtypeBAV")
l1 = paste(paste(paste(paste(paste("HR: ", paste(tt[a, 1], tt[a, 2], sep=" ("), sep="")), tt[a, 3], sep=", "), "); P=", sep=""), tt[a, 4], sep="")
jj = rbind(name, l1)
rownames(jj) = c("", "BAV")
colnames(jj) = ""
jj
}

##Load data
dfs = read.csv("/Users/jrigdon/Box sync/Rigdon/Priest/df_with_sensitivity_Nov5.csv", header=TRUE)

##Only keep variables we need
keep = c("CHDsubtype", "ACStime", "ISC_STROKEtime", "HFtime", "AFIBtime", "DEADtime", "ACSbin", "ISC_STROKEbin", "HFbin", "AFIBbin", "DEADbin", "Age_baseline", "Sex", "Townsend", "Caucasian", "Smoking", "Alcohol", "Low_activity", "Has_FHx_CVD", "BMI", "BP_systolic_AVG", "BP_diastolic_AVG", "hypertension_meds", "HLDprev", "DIABETESprev", "CS_First_Age")
dfs2 = dfs[, names(dfs) %in% keep]
#dfs2$remove = apply(dfs2[, names(dfs2) %in% c("DEADtime", "ACStime", "ISC_STROKEtime", "HFtime", "AFIBtime")], 1, function(x) sum(is.na(x))) #no 5s

##Define minimum time
dfs2$min_time = apply(dfs2[, names(dfs2) %in% c("ACStime", "ISC_STROKEtime", "HFtime", "AFIBtime", "DEADtime")], 1, function(x) min(x, na.rm=TRUE))

##Fix CHDsubtype variable
table(dfs2$CHDsubtype, exclude=NULL)
dfs2$CHDsubtype = as.character(dfs2$CHDsubtype)
dfs2$CHDsubtype[dfs2$CHDsubtype=="NON_SEVERE"] = "a.Non-severe"
table(dfs2$CHDsubtype, exclude=NULL)

##Define whether or not CS_First_Age happened within 1 year window of min_time
summary(dfs2$CS_First_Age)
summary(dfs2$min_time)
dfs2$lapse = dfs2$min_time-dfs2$CS_First_Age
dfs2$sens = 0
dfs2$sens[!is.na(dfs2$lapse) & dfs2$lapse>0 & dfs2$lapse<1] = 1
summary(dfs2$lapse[dfs2$sens==1])
table(dfs2$sens) #672 yes, 499317 no

##Define event_type and event_time for each data set
##ACS
dACS = dfs2
dACS$event_type = "a.Censor/death"
dACS$event_type[dACS$min_time==dACS$ISC_STROKEtime & !is.na(dACS$ISC_STROKEtime) & dACS$ISC_STROKEbin==1] = "ISC_STROKE"
dACS$event_type[dACS$min_time==dACS$HFtime & !is.na(dACS$HFtime) & dACS$HFbin==1] = "HF"
dACS$event_type[dACS$min_time==dACS$AFIBtime & !is.na(dACS$AFIBtime) & dACS$AFIBbin==1] = "AFIB"
dACS$event_type[dACS$min_time==dACS$ACStime & !is.na(dACS$ACStime) & dACS$ACSbin==1] = "ACS"
table(dACS$event_type)

##STROKE
dSTROKE = dfs2
dSTROKE$event_type = "a.Censor/death"
dSTROKE$event_type[dSTROKE$min_time==dSTROKE$HFtime & !is.na(dSTROKE$HFtime) & dSTROKE$HFbin==1] = "HF"
dSTROKE$event_type[dSTROKE$min_time==dSTROKE$AFIBtime & !is.na(dSTROKE$AFIBtime) & dSTROKE$AFIBbin==1] = "AFIB"
dSTROKE$event_type[dSTROKE$min_time==dSTROKE$ACStime & !is.na(dSTROKE$ACStime) & dSTROKE$ACSbin==1] = "ACS"
dSTROKE$event_type[dSTROKE$min_time==dSTROKE$ISC_STROKEtime & !is.na(dSTROKE$ISC_STROKEtime) & dSTROKE$ISC_STROKEbin==1] = "ISC_STROKE"
table(dSTROKE$event_type)

##HF
dHF = dfs2
dHF$event_type = "a.Censor/death"
dHF$event_type[dHF$min_time==dHF$AFIBtime & !is.na(dHF$AFIBtime) & dHF$AFIBbin==1] = "AFIB"
dHF$event_type[dHF$min_time==dHF$ACStime & !is.na(dHF$ACStime) & dHF$ACSbin==1] = "ACS"
dHF$event_type[dHF$min_time==dHF$ISC_STROKEtime & !is.na(dHF$ISC_STROKEtime) & dHF$ISC_STROKEbin==1] = "ISC_STROKE"
dHF$event_type[dHF$min_time==dHF$HFtime & !is.na(dHF$HFtime) & dHF$HFbin==1] = "HF"
table(dHF$event_type)

##AFIB
dAFIB = dfs2
dAFIB$event_type = "a.Censor/death"
dAFIB$event_type[dAFIB$min_time==dAFIB$ACStime & !is.na(dAFIB$ACStime) & dAFIB$ACSbin==1] = "ACS"
dAFIB$event_type[dAFIB$min_time==dAFIB$ISC_STROKEtime & !is.na(dAFIB$ISC_STROKEtime) & dAFIB$ISC_STROKEbin==1] = "ISC_STROKE"
dAFIB$event_type[dAFIB$min_time==dAFIB$HFtime & !is.na(dAFIB$HFtime) & dAFIB$HFbin==1] = "HF"
dAFIB$event_type[dAFIB$min_time==dAFIB$AFIBtime & !is.na(dAFIB$AFIBtime) & dAFIB$AFIBbin==1] = "AFIB"
table(dAFIB$event_type)

##Fix the min_time to min_time-(Age_baseline-10)
dACS$event_time = dACS$min_time-(dACS$Age_baseline-10)
dSTROKE$event_time = dSTROKE$min_time-(dSTROKE$Age_baseline-10)
dHF$event_time = dHF$min_time-(dHF$Age_baseline-10)
dAFIB$event_time = dAFIB$min_time-(dAFIB$Age_baseline-10)

##Only keep positive event_times
dACS = dACS[dACS$event_time>=0, ]
dSTROKE = dSTROKE[dSTROKE$event_time>=0, ]
dHF = dHF[dHF$event_time>=0, ]
dAFIB = dAFIB[dAFIB$event_time>=0, ]

##Look at event_type variable in each data set
table(dACS$event_type, exclude=NULL)
table(dSTROKE$event_type, exclude=NULL)
table(dHF$event_type, exclude=NULL)
table(dAFIB$event_type, exclude=NULL)

##Cross check the event_type variable with DEADbin, CADbin, ISC_STROKEbin, HFbin, AFIBbin
table(dACS$event_type, dACS$ACSbin)
table(dSTROKE$event_type, dSTROKE$ISC_STROKEbin)
table(dHF$event_type, dHF$HFbin)
table(dAFIB$event_type, dAFIB$AFIBbin)

##Table of CHDsubtype by outcome in each data set
table(dACS$CHDsubtype, exclude=NULL)
table(dACS$CHDsubtype, dACS$event_type, exclude=NULL)
table(dSTROKE$CHDsubtype, dSTROKE$event_type, exclude=NULL)
table(dHF$CHDsubtype, dHF$event_type, exclude=NULL)
table(dAFIB$CHDsubtype, dAFIB$event_type, exclude=NULL)


##Competing risks models

##2A: Therneau unadjusted for each outcome
T2a_ACS = coxph(Surv(event_time, event_type=="ACS")~CHDsubtype, data=dACS)
T2a_isc_stroke = coxph(Surv(event_time, event_type=="ISC_STROKE")~CHDsubtype, data=dSTROKE)
T2a_HF = coxph(Surv(event_time, event_type=="HF")~CHDsubtype, data=dHF)
T2a_AFIB = coxph(Surv(event_time, event_type=="AFIB")~CHDsubtype, data=dAFIB)

tab2A = rbind(getCR(T2a_ACS, "ACS"), getCR(T2a_isc_stroke, "isc_stroke"), getCR(T2a_HF, "HF"), getCR(T2a_AFIB, "AFIB"))


##2B: Therneau simple adjusted
T2b_ACS = coxph(Surv(event_time, event_type=="ACS")~Age_baseline + Sex + Townsend + Caucasian + CHDsubtype, data=dACS)
T2b_isc_stroke = coxph(Surv(event_time, event_type=="ISC_STROKE")~Age_baseline + Sex + Townsend + Caucasian + CHDsubtype, data=dSTROKE)
T2b_HF = coxph(Surv(event_time, event_type=="HF")~Age_baseline + Sex + Townsend + Caucasian + CHDsubtype, data=dHF)
T2b_AFIB = coxph(Surv(event_time, event_type=="AFIB")~Age_baseline + Sex + Townsend + Caucasian + CHDsubtype, data=dAFIB)

tab2B = rbind(getCR(T2b_ACS, "ACS"), getCR(T2b_isc_stroke, "isc_stroke"), getCR(T2b_HF, "HF"), getCR(T2b_AFIB, "AFIB"))

##2C: Therneau multivariable adjusted (predictor of CHD??)
##Make sure the adjustment variables are correct (look at Excel file)
T2c_ACS = coxph(Surv(event_time, event_type=="ACS")~Age_baseline + Sex + Townsend + Caucasian + Smoking + Alcohol + Low_activity + Has_FHx_CVD + BMI + BP_systolic_AVG + BP_diastolic_AVG + hypertension_meds + HLDprev + DIABETESprev + CHDsubtype, data=dACS)
T2c_isc_stroke = coxph(Surv(event_time, event_type=="ISC_STROKE")~Age_baseline + Sex + Townsend + Caucasian + Smoking + Alcohol + Low_activity + Has_FHx_CVD + BMI + BP_systolic_AVG + BP_diastolic_AVG + hypertension_meds + HLDprev + DIABETESprev + CHDsubtype, data=dSTROKE)
T2c_HF = coxph(Surv(event_time, event_type=="HF")~Age_baseline + Sex + Townsend + Caucasian + Smoking + Alcohol + Low_activity + Has_FHx_CVD + BMI + BP_systolic_AVG + BP_diastolic_AVG + hypertension_meds + HLDprev + DIABETESprev + CHDsubtype, data=dHF)
T2c_AFIB = coxph(Surv(event_time, event_type=="AFIB")~Age_baseline + Sex + Townsend + Caucasian + Smoking + Alcohol + Low_activity + Has_FHx_CVD + BMI + BP_systolic_AVG + BP_diastolic_AVG + hypertension_meds + HLDprev + DIABETESprev + CHDsubtype, data=dAFIB)

tab2C = rbind(getCR(T2c_ACS, "ACS"), getCR(T2c_isc_stroke, "isc_stroke"), getCR(T2c_HF, "HF"), getCR(T2c_AFIB, "AFIB"))

##Save multistate
word.doc(obj.list=list(tab2A, tab2B, tab2C), obj.title=c("Table 1: Multistate unadjusted", "Table 2: Multistate simple adjusted", "Table 3: Multistate adjusted"), dest="/Users/jrigdon/Box sync/Rigdon/Priest/Multistate_tables_2018-11-26_BAV.docx", ftype="Arial", col.odd="white")

##Sensitivity analyses by presence or absence of cardiac surgery one year prior to event of interest
##Absence
dACS1 = dACS[dACS$sens==0, ] #545 individuals
dSTROKE1 = dSTROKE[dSTROKE$sens==0, ]
dHF1 = dHF[dHF$sens==0, ]
dAFIB1 = dAFIB[dAFIB$sens==0, ]

##Competing risks models

##2A: Therneau unadjusted for each outcome
TSa_ACS = coxph(Surv(event_time, event_type=="ACS")~CHDsubtype, data=dACS1)
TSa_isc_stroke = coxph(Surv(event_time, event_type=="ISC_STROKE")~CHDsubtype, data=dSTROKE1)
TSa_HF = coxph(Surv(event_time, event_type=="HF")~CHDsubtype, data=dHF1)
TSa_AFIB = coxph(Surv(event_time, event_type=="AFIB")~CHDsubtype, data=dAFIB1)

tabSA = rbind(getCR(TSa_ACS, "ACS"), getCR(TSa_isc_stroke, "isc_stroke"), getCR(TSa_HF, "HF"), getCR(TSa_AFIB, "AFIB"))


##2B: Therneau simple adjusted
TSb_ACS = coxph(Surv(event_time, event_type=="ACS")~Age_baseline + Sex + Townsend + Caucasian + CHDsubtype, data=dACS1)
TSb_isc_stroke = coxph(Surv(event_time, event_type=="ISC_STROKE")~Age_baseline + Sex + Townsend + Caucasian + CHDsubtype, data=dSTROKE1)
TSb_HF = coxph(Surv(event_time, event_type=="HF")~Age_baseline + Sex + Townsend + Caucasian + CHDsubtype, data=dHF1)
TSb_AFIB = coxph(Surv(event_time, event_type=="AFIB")~Age_baseline + Sex + Townsend + Caucasian + CHDsubtype, data=dAFIB1)

tabSB = rbind(getCR(TSb_ACS, "ACS"), getCR(TSb_isc_stroke, "isc_stroke"), getCR(TSb_HF, "HF"), getCR(TSb_AFIB, "AFIB"))

##2C: Therneau multivariable adjusted (predictor of CHD??)
##Make sure the adjustment variables are correct (look at Excel file)
TSc_ACS = coxph(Surv(event_time, event_type=="ACS")~Age_baseline + Sex + Townsend + Caucasian + Smoking + Alcohol + Low_activity + Has_FHx_CVD + BMI + BP_systolic_AVG + BP_diastolic_AVG + hypertension_meds + HLDprev + DIABETESprev + CHDsubtype, data=dACS1)
TSc_isc_stroke = coxph(Surv(event_time, event_type=="ISC_STROKE")~Age_baseline + Sex + Townsend + Caucasian + Smoking + Alcohol + Low_activity + Has_FHx_CVD + BMI + BP_systolic_AVG + BP_diastolic_AVG + hypertension_meds + HLDprev + DIABETESprev + CHDsubtype, data=dSTROKE1)
TSc_HF = coxph(Surv(event_time, event_type=="HF")~Age_baseline + Sex + Townsend + Caucasian + Smoking + Alcohol + Low_activity + Has_FHx_CVD + BMI + BP_systolic_AVG + BP_diastolic_AVG + hypertension_meds + HLDprev + DIABETESprev + CHDsubtype, data=dHF1)
TSc_AFIB = coxph(Surv(event_time, event_type=="AFIB")~Age_baseline + Sex + Townsend + Caucasian + Smoking + Alcohol + Low_activity + Has_FHx_CVD + BMI + BP_systolic_AVG + BP_diastolic_AVG + hypertension_meds + HLDprev + DIABETESprev + CHDsubtype, data=dAFIB1)

tabSC = rbind(getCR(TSc_ACS, "ACS"), getCR(TSc_isc_stroke, "isc_stroke"), getCR(TSc_HF, "HF"), getCR(TSc_AFIB, "AFIB"))

##Save multistate
word.doc(obj.list=list(tabSA, tabSB, tabSC), obj.title=c("Table 1: Multistate unadjusted sensitivity", "Table 2: Multistate simple adjusted sensitivyt", "Table 3: Multistate adjusted sensitivity"), dest="/Users/jrigdon/Box sync/Rigdon/Priest/Multistate_tables_2018-11-26_BAV_sensitivity.docx", ftype="Arial", col.odd="white")

##Number of events in each condition
table(dAFIB1$CHDsubtype, exclude=NULL)

table(dACS1$CHDsubtype, dACS1$event_type, exclude=NULL)
table(dSTROKE1$CHDsubtype, dSTROKE1$event_type, exclude=NULL)
table(dHF1$CHDsubtype, dHF1$event_type, exclude=NULL)
table(dAFIB1$CHDsubtype, dAFIB1$event_type, exclude=NULL)


##Presence
dACS2 = dACS[dACS$sens==1, ] #545 individuals
dSTROKE2 = dSTROKE[dSTROKE$sens==1, ]
dHF2 = dHF[dHF$sens==1, ]
dAFIB2 = dAFIB[dAFIB$sens==1, ]

##Competing risks models

##2A: Therneau unadjusted for each outcome
TSa_ACS = coxph(Surv(event_time, event_type=="ACS")~CHDsubtype, data=dACS2)
TSa_isc_stroke = coxph(Surv(event_time, event_type=="ISC_STROKE")~CHDsubtype, data=dSTROKE2)
TSa_HF = coxph(Surv(event_time, event_type=="HF")~CHDsubtype, data=dHF2)
TSa_AFIB = coxph(Surv(event_time, event_type=="AFIB")~CHDsubtype, data=dAFIB2)

tabSA = rbind(getCR(TSa_ACS, "ACS"), getCR(TSa_isc_stroke, "isc_stroke"), getCR(TSa_HF, "HF"), getCR(TSa_AFIB, "AFIB"))


##2B: Therneau simple adjusted
TSb_ACS = coxph(Surv(event_time, event_type=="ACS")~Age_baseline + Sex + Townsend + Caucasian + CHDsubtype, data=dACS2)
TSb_isc_stroke = coxph(Surv(event_time, event_type=="ISC_STROKE")~Age_baseline + Sex + Townsend + Caucasian + CHDsubtype, data=dSTROKE2)
TSb_HF = coxph(Surv(event_time, event_type=="HF")~Age_baseline + Sex + Townsend + Caucasian + CHDsubtype, data=dHF2)
TSb_AFIB = coxph(Surv(event_time, event_type=="AFIB")~Age_baseline + Sex + Townsend + Caucasian + CHDsubtype, data=dAFIB2)

tabSB = rbind(getCR(TSb_ACS, "ACS"), getCR(TSb_isc_stroke, "isc_stroke"), getCR(TSb_HF, "HF"), getCR(TSb_AFIB, "AFIB"))

##2C: Therneau multivariable adjusted (predictor of CHD??)
##Make sure the adjustment variables are correct (look at Excel file)
TSc_ACS = coxph(Surv(event_time, event_type=="ACS")~Age_baseline + Sex + Townsend + Caucasian + Smoking + Alcohol + Low_activity + Has_FHx_CVD + BMI + BP_systolic_AVG + BP_diastolic_AVG + hypertension_meds + HLDprev + DIABETESprev + CHDsubtype, data=dACS2)
TSc_isc_stroke = coxph(Surv(event_time, event_type=="ISC_STROKE")~Age_baseline + Sex + Townsend + Caucasian + Smoking + Alcohol + Low_activity + Has_FHx_CVD + BMI + BP_systolic_AVG + BP_diastolic_AVG + hypertension_meds + HLDprev + DIABETESprev + CHDsubtype, data=dSTROKE2)
TSc_HF = coxph(Surv(event_time, event_type=="HF")~Age_baseline + Sex + Townsend + Caucasian + Smoking + Alcohol + Low_activity + Has_FHx_CVD + BMI + BP_systolic_AVG + BP_diastolic_AVG + hypertension_meds + HLDprev + DIABETESprev + CHDsubtype, data=dHF2)
TSc_AFIB = coxph(Surv(event_time, event_type=="AFIB")~Age_baseline + Sex + Townsend + Caucasian + Smoking + Alcohol + Low_activity + Has_FHx_CVD + BMI + BP_systolic_AVG + BP_diastolic_AVG + hypertension_meds + HLDprev + DIABETESprev + CHDsubtype, data=dAFIB2)

tabSC = rbind(getCR(TSc_ACS, "ACS"), getCR(TSc_isc_stroke, "isc_stroke"), getCR(TSc_HF, "HF"), getCR(TSc_AFIB, "AFIB"))

##Save multistate
word.doc(obj.list=list(tabSA, tabSB, tabSC), obj.title=c("Table 1: Multistate unadjusted sensitivity", "Table 2: Multistate simple adjusted sensitivyt", "Table 3: Multistate adjusted sensitivity"), dest="/Users/jrigdon/Box sync/Rigdon/Priest/Multistate_tables_2018-11-16_sensitivity.docx", ftype="Arial", col.odd="white")

##Number of events in each condition
table(dAFIB2$CHDsubtype, exclude=NULL)

table(dACS2$CHDsubtype, dACS2$event_type, exclude=NULL)
table(dSTROKE2$CHDsubtype, dSTROKE2$event_type, exclude=NULL)
table(dHF2$CHDsubtype, dHF2$event_type, exclude=NULL)
table(dAFIB2$CHDsubtype, dAFIB2$event_type, exclude=NULL)


