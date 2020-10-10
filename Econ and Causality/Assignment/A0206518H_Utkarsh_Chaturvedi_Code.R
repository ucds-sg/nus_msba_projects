Data <- read.csv("C:/Users/utkar/Desktop/MSBA/Lecture/DSC5101 - Analytics in Managerial Econ/Assignment/rewardDF.csv")


#comb = c(0.1,0.3,0.5,0.95)

len = 4
Target_pop = 10000
#len = length(comb)
play = 0
#Total_Donation=0

####UCB1
u = c(0,0,0,0)
uPlus = c(0,0,0,0)

n = c(0,0,0,0)

###initial run 

for(i in 1:len)
{
  u[i]=Data[i,j]
  n[i]=n[i]+1
}

#Total_Donation=sum(u)*21
arm_pulled <- vector()

##UCB implementing code
for(i in 1:(Target_pop-len))
{
  #if(i%%100000==0)
  #{print(i)}
  for(j in 1:len)
  {
    uPlus[j]=u[j]+sqrt(2 * log10(i)/n[j])
  }
  index=which.max(uPlus)
  arm_pulled[i]=index
  play=Data[i,j]
#  Total_Donation=Total_Donation + play*21
  u[index]=(u[index]*n[index]+play)/(n[index] + 1)
  n[index] = n[index] + 1
}

