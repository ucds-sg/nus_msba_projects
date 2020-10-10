#install.packages("dplyr")
library(dplyr)


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
  summarise(Affect = mean(bhc_avgtradingratio, na.rm = T))
Data_org
Reg_simple_1a <- lm(bhc_avgtradingratio ~ after_DFA_1, data = Data_org)
summary(Reg_simple_1a)

Reg_simple_1b <- lm(bhc_avgtradingratio ~ after_DFA_1 + dep_lnassets + dep_leverage + dep_roa1 + dep_liquidity + dep_depositratio + dep_cir + dep_creditrisk_total3 + dep_loans_REratio + dep_cpp_bankquarter, data = Data)
summary(Reg_simple_1b)

Reg_simple_1b1 <- lm(bhc_avgtradingratio ~ after_DFA_1 + dep_lnassets + dep_leverage + dep_depositratio + dep_cir + dep_creditrisk_total3 + dep_loans_REratio + dep_cpp_bankquarter, data = Data)
summary(Reg_simple_1b1)


Reg_simple_1c <- lm(bhc_avgtradingratio ~ after_DFA_1 + treat_3_b_avg + did+ dep_lnassets + dep_leverage + dep_roa1 + dep_liquidity + dep_depositratio + dep_cir + dep_creditrisk_total3 + dep_loans_REratio + dep_cpp_bankquarter, data = Data)
summary(Reg_simple_1c)

Reg_simple_1c1 <- lm(bhc_avgtradingratio ~ after_DFA_1 + treat_3_b_avg + did+ dep_lnassets + dep_leverage + dep_roa1 + dep_liquidity + dep_depositratio + dep_cir + dep_creditrisk_total3 + dep_loans_REratio + dep_cpp_bankquarter, data = Data)
summary(Reg_simple_1c1)

Reg_simple_1d <- lm(bhc_avgtradingratio ~  did+ dep_lnassets + dep_leverage  + dep_liquidity + dep_depositratio + dep_cir + dep_creditrisk_total3 + dep_loans_REratio + dep_cpp_bankquarter, data = Data)
summary(Reg_simple_1d)

dep_lnassets + dep_leverage + dep_roa1 + dep_liquidity + dep_depositratio + dep_cir + dep_creditrisk_total3 + dep_loans_REratio + dep_cpp_bankquarter
Reg_simple_2 <- lm(bhc_avgtradingratio ~ did, data = Data)
summary(Reg_simple_2)
