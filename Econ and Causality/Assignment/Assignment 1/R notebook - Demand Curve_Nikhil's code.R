#detach(package:plyr)
#library(dplyr)
#install.packages("AER")
library(AER)
library(ggplot2)

#library(plyr)
library(dplyr)
library(lattice)


data<-read.csv("Desktop/NUS MSBA/DSC5101 - Managerial Econ/Assignment /Project1Data.csv")
typeof(data)

data$dtd_bucket<- ifelse(data$dtd<=3,1,ifelse(data$dtd<=15,2,ifelse(data$dtd<=45,3,ifelse(data$dtd<=120,4,5))))
hist(data$dtd_bucket)
hist(data$dtd)

hist(data$num_bookings)
ggplot(data = data) + geom_histogram(aes(dtd)) + theme_bw()
bar_plot
bar_plot <- data%>%group_by(dtd_bucket)%>%
  summarise(Number_bookings = sum(num_bookings))
ggplot(data = bar_plot) + geom_bar(aes(x = dtd_bucket, y = Number_bookings), stat = "identity") + theme_bw()

ggplot2::ggplot(data = data) + geom_point(aes(x = dtd, y = price_ln, color = factor(dtd_bucket))) + theme_bw()



data%>%group_by(dtd_bucket)%>%summarise(sum(num_bookings))
data$price_ln<-log(data$mean_net_ticket_price)
data$num_ln<-log(data$num_bookings)


boxplot(data$mean_net_ticket_price)

boxplot(data$dtd)
boxplot(data$dtd_bucket)

colnames(data)

dt_OLS = lm(price_ln~dtd, data = data)
summary(dt_OLS)


dt_buc_OLS = lm(price_ln~dtd_bucket, data = data)
summary(dt_buc_OLS)


##cluster 1
#OLS 
d1<-data%>%filter(dtd_bucket ==1)
#m1_OLS = lm(num_ln~price_ln, data = d1)
#summary(m1_OLS)

m1_2sls<- ivreg(formula = num_ln~price_ln|inv, data = d1,na.omit = T)

summary(m1_2sls,diagnostics = T)
##cluster 2
#OLS 
d2<-data%>%filter(dtd_bucket ==2)
#m2_OLS = lm(num_ln~price_ln, data = d2)
#summary(m2_OLS)

m2_2sls<- ivreg(formula = num_ln~price_ln|inv, data = d2,na.omit = T)

summary(m2_2sls,diagnostics = T)

##cluster 3
#OLS 
d3<-data%>%filter(dtd_bucket ==3)
#m3_OLS = lm(num_ln~price_ln, data = d3)
#summary(m3_OLS)

m3_2sls<- ivreg(formula = num_ln~price_ln|inv, data = d3,na.omit = T)

summary(m3_2sls,diagnostics = T)
##cluster 4
#OLS 
d4<-data%>%filter(dtd_bucket ==4)
#m4_OLS = lm(num_ln~price_ln, data = d4)
#summary(m4_OLS)

m4_2sls<- ivreg(formula = num_ln~price_ln|inv, data = d4,na.omit = T)

summary(m4_2sls,diagnostics = T)
##cluster 5
#OLS 
d5<-data%>%filter(dtd_bucket ==5)
#m5_OLS = lm(num_ln~price_ln, data = d5)
#summary(m5_OLS)

m5_2sls<- ivreg(formula = num_ln~price_ln|inv, data = d5,na.omit = T)

summary(m5_2sls,diagnostics = T)

