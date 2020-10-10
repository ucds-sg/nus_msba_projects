#all the rewards are to be read from the csv
#if the read fails you may have to give full path
rewards <- read.csv("C:/Users/utkar/Desktop/MSBA/Lecture/DSC5101 - Analytics in Managerial Econ/Assignment/rewardDF.csv")
#total time periods
t<-10000
#total number of arms
narms <-4
#UCB variables initializations
n.j <- rep(0,4) 
mu.j <- rep(0,4)
mu.j.ucb <- rep(0,4)

#Pull every arm 1 time
for(armIdx in 1:4){
  n.j[armIdx] <- n.j[armIdx] + 1
  mu.j[armIdx] <- rewards[armIdx, armIdx] #Example pull arm 3 at time 3
}


for (tcount in 5:t) {
  #YOUR UCB IMPLEMENTATION GOES HERE!!!
}



  
