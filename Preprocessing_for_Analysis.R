##Author: Priyanka Saha

library(dplyr)
library(tidyr)
library(broom)
library(readr)
library(stringr)
library(ggplot2)

####
#OUTPUT OF THIS SCRIPT IS CONTAINED IN UKB_1/DATASETS/ as Basic_attributes_and_CVD_survival_allUKB_***.csv
####

#Load dataset with all eventtimes for cardiovascular outcomes.
#value of 1000 indicates no occurrence of the event.
#value of 2000 indicates occurrence of event but no date available for time of occurrence. Will treat these as missing values.
eventtimes <- read.csv("UKB_1/Datasets/Basic_attributes_CVD_survival_files/ComorbidityPhenotypes_v5_FirstAge.csv", sep = ",", header = TRUE) %>% select(-X)
eventtimes[eventtimes == 2000] <- NA #As mentioned above, 2000 indicates missing date for event, so treat as missing value.

##Load death data for times of death caused by first occurrence of a CVD outcome. 
death_data <- read.csv("UKB_1/Datasets/Basic_attributes_CVD_survival_files/Death_Diagnoses_Nov05_18.csv", sep = ",", header = T) %>%
  mutate_at(vars(Death_HF:Death_PREV_CAD), funs(as.factor))

#Load covariates (age, sex, year of birth, smoking, etc etc.)
covariates <- read.csv("UKB_1/Datasets/Basic_attributes_CVD_survival_files/basic_patient_attributes_May17.csv", sep = ",", header = TRUE)

#Join the covariates with eventtimes.
covar <- left_join(covariates, eventtimes,by="Patient_ID") %>%
  left_join(death_data, by = "Patient_ID")


###
#Subset the meds and diabetes related variables in preparation for dealing with NA's in next step.
meds_and_diabetes <- covar %>% select(Patient_ID, starts_with("Medication"), starts_with("Diabetes"), Early_insulin_use)

#Convert NA's and <0 values to 1000 to indicate that response is unavailable. Cannot retain NA in cell because R will treat
#NA's improperly in later cleaning steps.
meds_and_diabetes[is.na(meds_and_diabetes)] <- 1000
meds_and_diabetes[meds_and_diabetes < 0] <- 1000

#Rejoin the meds and diabetes variables with the variables data
covar <- covar %>%
  select(-c(starts_with("Medication"), starts_with("Diabetes"), Early_insulin_use)) %>%
  left_join(meds_and_diabetes, by = "Patient_ID")

covar2 <- covar %>%
  mutate(diabetes_indicator = ifelse(Medication_male_0 == 3 | 
                                       Medication_male_1 == 3 | 
                                       Medication_male_2 == 3 | 
                                       Medication_female_0 == 3 | 
                                       Medication_female_1 == 3 | 
                                       Medication_female_2 == 3 | 
                                       Medication_female_3 ==3 |
                                       Diabetes_by_doctor == 1, 1, 0)) %>% #if takes insulin or told by doctor that has diabetes, then indicator positive for diabetes
  mutate(T2D = ifelse((is.na(T2D) | T2D == 1000) & (is.na(T1D) | T1D == 1000) & diabetes_indicator == 1 & Diabetes_age >35, Diabetes_age, T2D)) %>%
  #if ICD codes do not indicate diagnosis of T1D or T2D but diabetes_indicator is positive for diabetes AND diabetes_age (age at which diabetes was diagnosed) 
  #is over 35 (per Stefan's definition), then assign diabetes age to T2D column.
  mutate(T1D = ifelse((is.na(T2D) | T2D == 1000) & (is.na(T1D) | T1D == 1000) & diabetes_indicator == 1 & Diabetes_age <=35, Diabetes_age, T1D)) %>%
  #if ICD codes do not indicate diagnosis of T1D or T2D but diabetes_indicator is positive for diabetes AND diabetes_age (age at which diabetes was diagnosed) 
  #is less than or equal to 35, then assign diabetes age to T1D column.
  mutate(T1D_new = ifelse(!is.na(T1D) & !is.na(T2D) & T1D <1000 & T2D <1000, 2000, T1D), #if positive for both T1D and T2D, then mark as 2000 (indicator for NA) because unable to determine true diagnosis.
         T2D_new = ifelse((!is.na(T1D) & !is.na(T2D) & T1D <1000 & T2D <1000) |
                            Early_insulin_use == 1, 2000, T2D)) %>%
         #per Stefan's definition, if used insulin within 1 year of diagnosis, then assume NOT T2DM.
  #combine the individual BP measurements (from auto and manual reads) into an average reading for systolic and diastolic
  mutate(hypertension_indicator = ifelse((!is.na(BP_systolic_AVG) & BP_systolic_AVG >= 140) | 
                                           (!is.na(BP_systolic_AVG) &BP_diastolic_AVG >= 90) | 
                                           Medication_male_0 == 2 | 
                                           Medication_male_1 == 2 | 
                                           Medication_female_0 == 2 | 
                                           Medication_female_1 == 2 | 
                                           Medication_female_2 == 2 | 
                                           Medication_female_3 ==2, 1, 0),
         #Hypertension indicator is positive (=1) if SBP >=140 or DBP >= 90 or taking hypertension meds
         hypertension_meds = ifelse(Medication_male_0 == 2 | 
                                      Medication_male_1 == 2 | 
                                      Medication_female_0 == 2 | 
                                      Medication_female_1 == 2 | 
                                      Medication_female_2 == 2 | 
                                      Medication_female_3 ==2, 1, 0),
         #Hypertension meds indicator is positive if taking hypertension meds
         hld_indicator = ifelse(Medication_male_0 == 1 | 
                                  Medication_male_1 == 1 | 
                                  Medication_female_0 == 1 | 
                                  Medication_female_1 == 1 | 
                                  Medication_female_2 == 1 |
                                  Medication_female_3 ==1, 1, 0))
          #Hyperlipidemia indicator is positive if taking statin

covar2[covar2 == 2000] <- NA
#convert 2000 (placeholder for NA) to NA


##Prepare the PREVALENCE variables - Prevalence of outcomes at baseline enrollment.
covar3 <- covar2 %>%
  mutate(Age_baseline = Age_At_Recruitment_0_0,
         Sex = as.factor(Sex_0_0),
         Year_Of_Birth = Year_Of_Birth_0_0,
         Smoking = as.factor(ifelse(Current_smoking_status_0 == "" | Current_smoking_status_0 == "missing", NA, as.character(Current_smoking_status_0))),
         Alcohol = as.factor(ifelse(Alcohol_intake_0 == "" | Alcohol_intake_0 == "missing", NA, as.character(Alcohol_intake_0))),
         Caucasian = as.factor(ifelse(Self_Reported_Ethnicity == 1 | Self_Reported_Ethnicity == 1001 | Self_Reported_Ethnicity ==1002 | Self_Reported_Ethnicity == 1003, 1, 0)),
         Townsend = Townsend_deprivation,
         Weight = as.factor(ifelse(BMI >=30, "Obese", "Non-obese")),
         Has_FHx_CVD = as.factor(ifelse(Maternal_CVD == 1 | Paternal_CVD ==1, 1, 0)),
         FEV1_avg = rowMeans(select(covar2, starts_with("FEV1")), na.rm = T),
         FVC_avg = rowMeans(select(covar2, starts_with("FVC")), na.rm = T),
         PEF_avg = rowMeans(select(covar2, starts_with("PEF")), na.rm = T),
         Max.HR = Max.HR_0,
         Max.workload = Max.Workload_0,
         Handgrip = Hand.grip.strength_0,
         Household_income = as.factor(ifelse(Avg_houseincome_pretax_0 == "" | Avg_houseincome_pretax_0 == "missing", NA, Avg_houseincome_pretax_0)),
         Maternal_Smoking_Around_Birth = as.factor(ifelse(Maternal_Smoking_Around_Birth <0, NA, Maternal_Smoking_Around_Birth)),
         Birthweight = Birth.weight..kg.,
         Vigorous.exercise = ifelse(Vigorous.exercise_0 < 0, NA, Vigorous.exercise_0),
         Moderate.exercise = ifelse(Moderate.exercise_0 < 0, NA, Moderate.exercise_0),
         Low_activity = as.factor(ifelse(Vigorous.exercise <3 & Moderate.exercise <5, 1, 0)) ## using & in the logic here is the "alternative definition" for physical activity per file name
         ) %>%
  mutate(Smoking = relevel(Smoking, "Never"),
         Alcohol = relevel(Alcohol, "Seldom"),
         Weight = relevel(Weight, "Non-obese")) %>%
  mutate(MACEprev = as.factor(ifelse(CV_COMPOSITE <= Age_baseline & CV_COMPOSITE >0, 1, 0)),
         CADprev = as.factor(ifelse(PREV_CAD <= Age_baseline & PREV_CAD >0, 1, 0)),
         AllCADprev = as.factor(ifelse(PREV_CAD <=Age_baseline & PREV_CAD>0, 1, 0)),
         ISC_STROKEprev = as.factor(ifelse(ISC_STROKE <= Age_baseline & ISC_STROKE >0, 1, 0)),
         HEM_STROKEprev = as.factor(ifelse(HEM_STROKE <= Age_baseline & HEM_STROKE >0, 1, 0)),
         ALL_STROKEprev = as.factor(ifelse(ALL_STROKE <= Age_baseline & ALL_STROKE >0, 1, 0)),
         HFprev = as.factor(ifelse(HF <= Age_baseline & HF >0, 1, 0)),
         AFIBprev = as.factor(ifelse(AFIB <= Age_baseline & AFIB >0, 1, 0)),
         T1Dprev = as.factor(ifelse(T1D_new <= Age_baseline & T1D_new >0, 1, 0)),
         T2Dprev = as.factor(ifelse(T2D_new <= Age_baseline & T2D_new >0, 1, 0)),
         DIABETESprev = as.factor(ifelse((!is.na(T1D) & T1D <= Age_baseline) | (!is.na(T2D) & T2D <= Age_baseline), 1, 0)),
         HTNprev = as.factor(ifelse(hypertension_indicator == 1 | (HYPERTENSION>0 & HYPERTENSION <= Age_baseline), 1, 0)),
         HLDprev = as.factor(ifelse(hld_indicator == 1 | (HYPERLIPIDEMIA>0 & HYPERLIPIDEMIA <= Age_baseline), 1, 0))
  ) %>%
##Prepare the SURVIVAL variables -- time (in years of age since birth) to event.
  mutate(DEADbin = ifelse(!is.na(Age_at_death), 1, 0),
         MACEbin = ifelse(CV_COMPOSITE == 1000, 0, 1), #CV_COMPOSITE combines diagnostic codes for ACS, stroke, heart failure, and afib.
         CADbin = ifelse(INC_ACS == 1000, 0, 1),
         ACSbin = ifelse(ACS == 1000, 0, 1), #ACS is CAD minus revascularization procedures (PCTA and CABG)
         AllCADbin = ifelse(PREV_CAD == 1000, 0, 1),
         ISC_STROKEbin = ifelse(ISC_STROKE == 1000, 0, 1),
         HFbin = ifelse(HF == 1000, 0, 1),
         AFIBbin = ifelse(AFIB == 1000, 0, 1)
  ) %>%
  mutate(DEADtime = as.numeric(ifelse(!is.na(Age_at_death), Age_at_death, 2017-Year_Of_Birth)),
         MACEtime = as.numeric(ifelse(MACEbin == 0 & !is.na(Age_at_death), Age_at_death,
                                      ifelse(MACEbin == 0 & is.na(Age_at_death), 2017-Year_Of_Birth, CV_COMPOSITE))),
         CADtime = as.numeric(ifelse(CADbin == 0 & !is.na(Age_at_death), Age_at_death,
                                     ifelse(CADbin == 0 & is.na(Age_at_death), 2017-Year_Of_Birth, INC_ACS))),
         ACStime = as.numeric(ifelse(ACSbin == 0 & !is.na(Age_at_death), Age_at_death,
                                          ifelse(ACSbin == 0 & is.na(Age_at_death), 2017-Year_Of_Birth, ACS))),
         AllCADtime = as.numeric(ifelse(AllCADbin == 0 & !is.na(Age_at_death), Age_at_death,
                                        ifelse(AllCADbin == 0 & is.na(Age_at_death), 2017-Year_Of_Birth, PREV_CAD))),
         ISC_STROKEtime = as.numeric(ifelse(ISC_STROKEbin == 0 & !is.na(Age_at_death), Age_at_death,
                                        ifelse(ISC_STROKEbin == 0 & is.na(Age_at_death), 2017-Year_Of_Birth, ISC_STROKE))),
         HFtime = as.numeric(ifelse(HFbin == 0 & !is.na(Age_at_death), Age_at_death,
                                    ifelse(HFbin == 0 & is.na(Age_at_death), 2017-Year_Of_Birth, HF))),
         AFIBtime = as.numeric(ifelse(AFIBbin == 0 & !is.na(Age_at_death), Age_at_death,
                                      ifelse(AFIBbin == 0 & is.na(Age_at_death), 2017-Year_Of_Birth, AFIB)))) %>%
  mutate(AFIBbeforeSTROKE = as.factor(ifelse(AFIBbin == 1 & ISC_STROKEbin ==1 & AFIBtime < ISC_STROKEtime, 1, 0)),
         AFIBbeforeCAD = as.factor(ifelse(AFIBbin == 1 & CADbin == 1 & AFIBtime < CADtime, 1, 0)),
         AFIBbeforeACS = as.factor(ifelse(AFIBbin == 1 & ACSbin == 1 & AFIBtime < ACStime, 1, 0)),
         AFIBbeforeHF = as.factor(ifelse(AFIBbin == 1 & HFbin == 1 & AFIBtime < HFtime, 1, 0)),
         CADbeforeHF = as.factor(ifelse(AllCADbin == 1 & HFbin == 1 & AllCADtime <HFtime, 1, 0)),
         CADbeforeAFIB = as.factor(ifelse(AllCADbin == 1 & AFIBbin == 1 & AllCADtime < AFIBtime, 1, 0)),
         HFbeforeAFIB = as.factor(ifelse(HFbin == 1 & AFIBbin == 1 & HFtime < AFIBtime, 1, 0))
         ) %>%
  #Correct binary variables for fatal occurrence of event.
  mutate(MACEbin = ifelse(MACEbin ==1 | Death_CV_COMPOSITE == 1, 1, 0),
         CADbin = ifelse(CADbin == 1 | Death_INC_ACS == 1, 1, 0),
         ACSbin = ifelse(ACSbin == 1 | Death_ACS == 1, 1, 0),
         AllCADbin = ifelse(AllCADbin == 1 | Death_PREV_CAD == 1, 1, 0),
         ISC_STROKEbin = ifelse(ISC_STROKEbin == 1 | Death_ISC_STROKE == 1, 1, 0),
         HFbin = ifelse(HFbin == 1 | Death_HF == 1, 1, 0),
         AFIBbin = ifelse(AFIBbin == 1 | Death_AFIB == 1, 1, 0))

covar4 <- covar3 %>%
  select(Patient_ID,
         Year_Of_Birth,
         Age_at_death,
         Age_baseline,
         Sex,
         Caucasian,
         Townsend,
         Country,
         Household_income,
         Height_cm,
         Weight_kg,
         BP_systolic_AVG,
         BP_diastolic_AVG,
         BMI,
         Birthweight,
         Maternal_Smoking_Around_Birth,
         Smoking,
         Alcohol,
         BMI,
         Weight,
         Has_FHx_CVD,
         Vigorous.exercise,
         Moderate.exercise,
         Low_activity,
         FEV1_avg,
         FVC_avg,
         PEF_avg,
         Max.HR,
         Max.workload,
         Handgrip,
         hypertension_meds,
         MACEprev:HLDprev,
         DEADbin:AFIBbin,
         DEADtime:AFIBtime,
         AFIBbeforeSTROKE:HFbeforeAFIB)

#Load patients to exclude due to drop out from study. See email from UKB from May 11, 2018.
excluded <- read.csv("UKB_1/Datasets/Basic_attributes_CVD_survival_files/excluded_15860_patients_051118.csv", sep = ",", header = T)

final <- anti_join(covar4, excluded, by = "Patient_ID") # Total of 502,616 participants.
  
