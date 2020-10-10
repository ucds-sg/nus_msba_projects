#install.packages("dplyr")
#install.packages("foreign")

#library(foreign)
#Panel <- read.dta("http://dss.princeton.edu/training/Panel101.dta")

library(dplyr)
library(tidyr)


Data_org<-read.csv("C:/Users/utkar/Desktop/MSBA/Lecture/DSC5101 - Analytics in Managerial Econ/Assignment/Assignment 2/Did_data.csv")

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
Reg_fixed_time <- plm(bhc_avgtradingratio ~ #after_DFA_1 + 
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
                 model = "within",
                 effect = "twoways")
summary(Reg_fixed_time)



############################## Panel B: (1) - not sure


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
                      replace = F
                      ) #one-on-one nearest neighbour matching
summary(Prop_matching)
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

