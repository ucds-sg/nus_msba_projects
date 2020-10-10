#########################################################################################################
# CODE: Econ Project 2: Analysis on Impact of DFA rule
# Author(s): Utkarsh
# Date: 25/10/2019
#########################################################################################################



#install.packages("dplyr")
#install.packages("foreign")

#library(foreign)
#Panel <- read.dta("http://dss.princeton.edu/training/Panel101.dta")

library(dplyr)
library(tidyr)


Data_org<-read.csv("C:/Users/utkar/Desktop/MSBA/Lecture/DSC5101 - Analytics in Managerial Econ/Assignment/Assignment 2/DiD_data.csv")

#Data_org$X<- NULL

summary(Data_org)
#Data <-Data_org %>% filter(!is.na(bhc_avgtradingratio))
#Data$did<-Data$treat_3_b_avg*Data$after_DFA_1
#summary(Data)
colnames(Data_org)

# Baseline tests
Data_affect <- Data_org %>% filter(rssd9999 <= 20090630) %>% 
  group_by(rssd9001) %>% 
  summarise(Affect = mean(bhc_avgtradingratio, na.rm = T)) %>% ungroup()

## Exercise for later - explore missing values
Missing_data_exploration <- Data_org %>% group_by(rssd9001,after_DFA_1) %>% 
  summarise(min_date = min(rssd9999, na.rm = T), max_date = max(rssd9999, na.rm = T)) %>% 
  pivot_wider(id_cols = rssd9001,names_from = after_DFA_1 ,values_from = c("min_date","max_date"))
  #spread(after_DFA_1,min_date) %>% 
  #spread(after_DFA_1,max_date) 
Data_org <- merge(Data_org,Data_affect, by = c("rssd9001"), all.x = T, all.y = F)

# Panel A:(1)
Reg_simple_1a <- lm(bhc_avgtradingratio ~ after_DFA_1, data = Data_org)
summary(Reg_simple_1a)


# Panel A:(2) -  Control variables comprise total assets, proﬁtability?????, leverage ratio, liquidity ratio, deposit ratio, NPL ratio, RE loan ratio, cost-income ratio, and an indicator variable that takes the value of one if the bank was a recipient of the TARP CPP program in a respective quarter
Reg_simple_1b <- lm(bhc_avgtradingratio ~ after_DFA_1 + 
                      dep_lnassets + 
                      dep_leverage + 
                      dep_liquidity + 
                      dep_depositratio + 
                      dep_creditrisk_total3 +
                      dep_loans_REratio +
                      dep_cir + 
                      dep_cpp_bankquarter + 
                      dep_roa1, ## profitability, 
                    data = Data_org)
summary(Reg_simple_1b)

# Panel A:(3)
Reg_1c <- lm(bhc_avgtradingratio ~ after_DFA_1 + 
                      dep_lnassets + 
                      dep_leverage + 
                      dep_liquidity + 
                      dep_depositratio + 
                      dep_creditrisk_total3 +
                      dep_loans_REratio +
                      dep_cir + 
                      dep_cpp_bankquarter + 
                      dep_roa1 + ## profitability,
                      Affect +
                      Affect*after_DFA_1,
                    data = Data_org)
summary(Reg_1c)


# Panel A:(4)
#install.packages("plm")
library(plm)
Reg_fixed <- plm(bhc_avgtradingratio ~ #after_DFA_1 + 
               dep_lnassets + 
               dep_leverage + 
               dep_liquidity + 
               dep_depositratio + 
               dep_creditrisk_total3 +
               dep_loans_REratio +
               dep_cir + 
               dep_cpp_bankquarter + 
               dep_roa1 + ## profitability,
               #Affect +
               Affect*after_DFA_1,
             data = Data_org,
             index = c("rssd9001","rssd9999"),
             model = "within")
summary(Reg_fixed)
fixef(Reg_fixed)

Reg_random <- plm(bhc_avgtradingratio ~ #after_DFA_1 + 
                   dep_lnassets + 
                   dep_leverage + 
                   dep_liquidity + 
                   dep_depositratio + 
                   dep_creditrisk_total3 +
                   dep_loans_REratio +
                   dep_cir + 
                   dep_cpp_bankquarter + 
                   dep_roa1 + ## profitability,
                   #Affect +
                   Affect*after_DFA_1,
                 data = Data_org,
                 index = c("rssd9001","rssd9999"),
                 model = "random")
summary(Reg_random)
#fixef(Reg_random)

## Testing whether fixed or random models are necessary
phtest(Reg_fixed, Reg_random)
#Hausman Test

#data:  bhc_avgtradingratio ~ dep_lnassets + dep_leverage + dep_liquidity +  ...
#chisq = 207.13, df = 11, p-value < 2.2e-16
#alternative hypothesis: one model is inconsistent

## From test, we conclude that fixed effects should be used

#### Testing whether time-fixed effects are necessary
Reg_fixed_time_test <- plm(bhc_avgtradingratio ~ #after_DFA_1 + 
                        dep_lnassets + 
                        dep_leverage + 
                        dep_liquidity + 
                        dep_depositratio + 
                        dep_creditrisk_total3 +
                        dep_loans_REratio +
                        dep_cir + 
                        dep_cpp_bankquarter + 
                        dep_roa1 + ## profitability,
                        #Affect +
                        Affect*after_DFA_1 +
                        factor(rssd9999),
                      data = Data_org,
                      index = c("rssd9001","rssd9999"),
                      model = "within")
# Significnace tests
pFtest(Reg_fixed_time_test,Reg_fixed) #p-value < 0.05
plmtest(Reg_fixed, c("time"), type=("bp")) #p-value < 0.05
# Conclusion: As assumed, time-fixed effects are in-fact necessary

# Panel A:(4) - final answer
Reg_fixed_time <- plm(bhc_avgtradingratio ~ after_DFA_1 + 
                   dep_lnassets + 
                   dep_leverage + 
                   dep_liquidity + 
                   dep_depositratio + 
                   dep_creditrisk_total3 +
                   dep_loans_REratio +
                   dep_cir + 
                   dep_cpp_bankquarter + 
                   dep_roa1 + ## profitability,
                   Affect +
                   Affect*after_DFA_1,
                 data = Data_org,
                 index = c("rssd9001","rssd9999"),
                 model = "within",
                 effect = "twoways")
summary(Reg_fixed_time)



############################## Panel B #########

# Panel B - (1)
Robust_test_1 <- plm(bhc_avgtradingratio ~ #after_DFA_1 + 
                       #treat_3_b_avg +
                        dep_lnassets + 
                        dep_leverage + 
                        dep_liquidity + 
                        dep_depositratio + 
                        dep_creditrisk_total3 +
                        dep_loans_REratio +
                        dep_cir + 
                        dep_cpp_bankquarter + 
                        dep_roa1 + ## profitability,
                        #Affect +
                        #Affect*after_DFA_1
                        after_DFA_1*treat_3_b_avg,
                      data = Data_org,
                      index = c("rssd9001","rssd9999"),
                      model = "within",
                      effect = "twoways")
summary(Robust_test_1)

# Panel B - propensity matching
#install.packages("MatchIt")
library(MatchIt)

Prop_matching_data <- Data_org %>% filter(complete.cases(.)) %>% filter(rssd9999 == 20040930)


Prop_matching <- matchit(treat_3_b_avg ~ #after_DFA_1 + 
                        dep_lnassets + 
                        dep_leverage + 
                        dep_liquidity + 
                        dep_depositratio + 
                        dep_creditrisk_total3 +
                        dep_loans_REratio +
                        dep_cir + 
                        dep_cpp_bankquarter + 
                        dep_roa1, #+ ## profitability,
                        #Affect +
                        #Affect*after_DFA_1,
                      data = Prop_matching_data,
                      distance = "logit",
                      method = "nearest",
                      model = "logit",
                      ratio = 3,
                      replace = T
                      ) #one-on-one nearest neighbour matching
Prop_summary <- summary(Prop_matching)
Prop_data <- match.data(Prop_matching)

Prop_data <- Data_org %>% filter(rssd9001 %in% c(unique(Prop_data$rssd9001)))
Prop_data <- Prop_data %>% filter(complete.cases(.))

## Matched sample result - ~1668 rows
Reg_Prop_matching <- plm(bhc_avgtradingratio ~ #after_DFA_1 + 
                        dep_lnassets + 
                        dep_leverage + 
                        dep_liquidity + 
                        dep_depositratio + 
                        dep_creditrisk_total3 +
                        dep_loans_REratio +
                        dep_cir + 
                        dep_cpp_bankquarter + 
                        dep_roa1 + ## profitability,
                        #Affect +
                        #Affect*after_DFA_1
                        after_DFA_1*treat_3_b_avg,
                      data = Prop_data,
                      index = c("rssd9001","rssd9999"),
                      model = "within",
                      effect = "twoways")
summary(Reg_Prop_matching)

## Full sample result -~40k rows

Reg_Prop_full_sample <- plm(bhc_avgtradingratio ~ #after_DFA_1 + 
                           dep_lnassets + 
                           dep_leverage + 
                           dep_liquidity + 
                           dep_depositratio + 
                           dep_creditrisk_total3 +
                           dep_loans_REratio +
                           dep_cir + 
                           dep_cpp_bankquarter + 
                           dep_roa1 + ## profitability,
                           #Affect +
                           #Affect*after_DFA_1
                           after_DFA_1*treat_3_b_avg,
                         data = Data_org,
                         index = c("rssd9001","rssd9999"),
                         model = "within",
                         effect = "twoways")
summary(Reg_Prop_full_sample)

# Panel B - Affect_pre_2007

Affect_pre_2007_Data <- Data_org %>% filter(rssd9999 <= 20061231 & rssd9999 >= 20030331) %>%
  group_by(rssd9001) %>%
  summarise(Affect_pre_2007 = mean(bhc_avgtradingratio, na.rm = T)) %>% ungroup()
Data_org <- merge(Data_org,Affect_pre_2007_Data, by = c("rssd9001"), all.x = T, all.y = F)

Robust_test_3<- plm(bhc_avgtradingratio ~ #after_DFA_1 + 
                              dep_lnassets + 
                              dep_leverage + 
                              dep_liquidity + 
                              dep_depositratio + 
                              dep_creditrisk_total3 +
                              dep_loans_REratio +
                              dep_cir + 
                              dep_cpp_bankquarter + 
                              dep_roa1 + ## profitability,
                              #Affect +
                              #Affect*after_DFA_1
                              after_DFA_1*Affect_pre_2007,
                            data = Data_org,
                            index = c("rssd9001","rssd9999"),
                            model = "within",
                            effect = "twoways")
summary(Robust_test_3)

# Panel B - Non-trading BHC's

Non_tradingBHC_data <- Data_org  %>% select(rssd9001,bhc_avgtradingratio,after_DFA_1) %>% 
  distinct() %>% group_by(rssd9001,after_DFA_1) %>% 
  summarise(max_trading_ratio = max(bhc_avgtradingratio, na.rm = T)) %>% ungroup() %>%
  spread(.,after_DFA_1,max_trading_ratio) %>%
  filter(`0` > 0 & `1`>0)

# Non_tradingBHC_data <- Data_org  %>% select(rssd9001,bhc_avgtradingratio) %>% 
#   distinct() %>% group_by(rssd9001) %>% 
#   summarise(max_trading_ratio = max(bhc_avgtradingratio, na.rm = T)) %>% ungroup() %>%
#   #spread(.,after_DFA_1,max_trading_ratio) %>%
#   filter(max_trading_ratio > 0)

Data_org_Trading_BHC <- Data_org[Data_org$rssd9001 %in% c(Non_tradingBHC_data$rssd9001),]

Robust_test_4<- plm(bhc_avgtradingratio ~ #after_DFA_1 + 
                      dep_lnassets + 
                      dep_leverage + 
                      dep_liquidity + 
                      dep_depositratio + 
                      dep_creditrisk_total3 +
                      dep_loans_REratio +
                      dep_cir + 
                      dep_cpp_bankquarter + 
                      dep_roa1 + ## profitability,
                      #Affect +
                      #Affect*after_DFA_1
                      after_DFA_1*Affect_pre_2007,
                    data = Data_org_Trading_BHC,
                    index = c("rssd9001","rssd9999"),
                    model = "within",
                    effect = "twoways")
summary(Robust_test_4)


# AppendixD - Test for linearity
Data_org$Affect_squared <- (Data_org$Affect)^2
Test_for_linearity_1 <- lm(bhc_avgtradingratio ~ after_DFA_1 + 
                                 dep_lnassets + 
                                 dep_leverage + 
                                 dep_liquidity + 
                                 dep_depositratio + 
                                 dep_creditrisk_total3 +
                                 dep_loans_REratio +
                                 dep_cir + 
                                 dep_cpp_bankquarter + 
                                 dep_roa1 + ## profitability,
                                 Affect +
                                 Affect_squared +
                                 Affect*after_DFA_1 + 
                                 Affect_squared*after_DFA_1
                               ,
                               data = Data_org)

summary(Test_for_linearity_1)

# FE controlled
Test_for_linearity_2 <- plm(bhc_avgtradingratio ~ after_DFA_1 + 
                        dep_lnassets + 
                        dep_leverage + 
                        dep_liquidity + 
                        dep_depositratio + 
                        dep_creditrisk_total3 +
                        dep_loans_REratio +
                        dep_cir + 
                        dep_cpp_bankquarter + 
                        dep_roa1 + ## profitability,
                        Affect +
                        Affect_squared +
                        Affect*after_DFA_1 + 
                        Affect_squared*after_DFA_1
                        ,
                      data = Data_org,
                      index = c("rssd9001","rssd9999"),
                      model = "within",
                      effect = "twoways")
summary(Test_for_linearity_2)


## Placebo effect - iteration 1

Before_dfa_quarters <- sort(unique(Data_org[Data_org$rssd9999 >= 20061231 & Data_org$rssd9999 <= 20090631,]$rssd9999))
Interaction_Coefficient = vector()
counter = 1

for (i in 1:length(Before_dfa_quarters)){
  quarter_selected = Before_dfa_quarters[i]
  Banks_selected <- Data_org %>% filter(Data_org$rssd9999==quarter_selected & 
                                          Data_org$bhc_avgtradingratio>0) %>% select(rssd9001) %>% distinct()
  for(j in 1:100){
  Banks_selected$New_Affected_BHC <- sample(c(0,1), replace = T, size = nrow(Banks_selected)) 
  Data_subset <- merge(Data_org,Banks_selected, by = c("rssd9001"), all.x = F, all.y = F)
  model <- plm(bhc_avgtradingratio ~ #after_DFA_1 + 
                             dep_lnassets + 
                             dep_leverage + 
                             dep_liquidity + 
                             dep_depositratio + 
                             dep_creditrisk_total3 +
                             dep_loans_REratio +
                             dep_cir + 
                             dep_cpp_bankquarter + 
                             dep_roa1 + ## profitability,
                             #Affect +
                             #Affect*after_DFA_1
                             after_DFA_1*New_Affected_BHC,
                           data = Data_subset,
                           index = c("rssd9001","rssd9999"),
                           model = "within",
                           effect = "twoways")
  coefficients <- coefficients(model)
  Interaction_Coefficient[counter] = coefficients['after_DFA_1:New_Affected_BHC']
  counter = counter + 1
  }
  counter = i*100 + 1
  #print(counter)
}


## Placebo effect - iteration 1

Before_dfa_quarters <- sort(unique(Data_org[Data_org$rssd9999 >= 20061231 & Data_org$rssd9999 <= 20090631,]$rssd9999))
Interaction_Coefficient = vector()
counter = 1

for (i in 1:length(Before_dfa_quarters)){
  quarter_selected = Before_dfa_quarters[i]
  Banks_selected <- Data_org %>% filter(Data_org$rssd9999==quarter_selected & 
                                          Data_org$bhc_avgtradingratio>0) %>% select(rssd9001) %>% distinct()
  for(j in 1:100){
    Banks_selected$New_Affected_BHC <- sample(c(0,1), replace = T, size = nrow(Banks_selected)) 
    Data_subset <- merge(Data_org,Banks_selected, by = c("rssd9001"), all.x = F, all.y = F)
    model <- plm(bhc_avgtradingratio ~ #after_DFA_1 + 
                   dep_lnassets + 
                   dep_leverage + 
                   dep_liquidity + 
                   dep_depositratio + 
                   dep_creditrisk_total3 +
                   dep_loans_REratio +
                   dep_cir + 
                   dep_cpp_bankquarter + 
                   dep_roa1 + ## profitability,
                   #Affect +
                   #Affect*after_DFA_1
                   after_DFA_1*New_Affected_BHC,
                 data = Data_subset,
                 index = c("rssd9001","rssd9999"),
                 model = "within",
                 effect = "twoways")
    coefficients <- coefficients(model)
    Interaction_Coefficient[counter] = coefficients['after_DFA_1:New_Affected_BHC']
    counter = counter + 1
  }
  counter = i*100 + 1
  #print(counter)
}
Interaction_Coefficient_dataframe <- as.data.frame(Interaction_Coefficient)

ggplot(Interaction_Coefficient_dataframe) + theme_bw() +
  geom_histogram(aes(x=Interaction_Coefficient, y=(..count..)/sum(..count..))) +
  labs(y="Percent",
       x="Frequency") + 
  facet_wrap( ~ Interaction_Coefficient)

ggplot(data = Interaction_Coefficient_dataframe, aes(x = Interaction_Coefficient)) + geom_histogram() +
  geom_vline(xintercept = -0.0289) +
  

## Iteration 2 - comparing current quarter to previous (NOT NEXT) quarter where current quarter is 1

## Verifying the strong effects experienced by BHC's

# Data_org$BHC_Categorisation <- ifelse(Data_org$Affect>=0.00 & Data_org$Affect<=0.02, ">2percent",
#                                       ifelse(Data_org$Affect>0.02 & Data_org$Affect<=0.03,">3percent",
#                                       ifelse(Data_org$Affect>0.03 & Data_org$Affect<=0.05,">5percent",
#                                       ifelse(Data_org$Affect>0.05 & Data_org$Affect<=0.10,">10percent",
#                                              ifelse(Data_org$Affect>0.10 & Data_org$Affect<=0.15,">15percent",
#                                       ">15percent")
# )
# )))

#table(Data_org$BHC_Categorisation )
#for (i in (1:length(unique(Data_org$BHC_Categorisation)))){

#Banks_BHC_Category_Filter <- Data_org[Data_org$BHC_Categorisation = unique(Data_org$BHC_Categorisation)[i]]
#print(unique(Data_org$BHC_Categorisation)[i])
# Treatment & Control
Data_org$treat_3_b_avg_new <- ifelse(Data_org$Affect > 0.005,
                                     1,0)
BHC_Affect_Confirm <- plm(bhc_avgtradingratio ~ #after_DFA_1 + 
                       #treat_3_b_avg +
                       dep_lnassets + 
                       dep_leverage + 
                       dep_liquidity + 
                       dep_depositratio + 
                       dep_creditrisk_total3 +
                       dep_loans_REratio +
                       dep_cir + 
                       dep_cpp_bankquarter + 
                       dep_roa1 + ## profitability,
                       #Affect +
                       #Affect*after_DFA_1
                       after_DFA_1*treat_3_b_avg_new,
                     data = Data_org[Data_org$Affect!= 0,],
                     index = c("rssd9001","rssd9999"),
                     model = "within",
                     effect = "twoways")
print(summary(BHC_Affect_Confirm))
#}

Test <- Data_org %>% select(rssd9001,BHC_Categorisation) %>% distinct()
table(Test$BHC_Categorisation)
