# -*- coding: utf-8 -*-
"""
Created on Sat Jul 31 14:49:19 2021

@author: Rohini
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 20:08:25 2021

@author: Rohini
"""
import numpy as np
from random import random
import pandas as pd

logFlows=X
transformedflows=np.exp(logFlows)
nYears=10000
AnnualQ_h = np.array(pd.read_csv('AnnualQ_Gunnison.csv',header=None))
MonthlyQ_h = np.array(pd.read_csv('MonthlyQ_Gunnison.csv',header=None))
historical_last_node = MonthlyQ_h[:,-1]
W=historical_last_node.reshape(105,12)

LastNodeFractions = np.zeros([105,12])
#Last node monthly fractions
for i in range(105):
    LastNodeFractions[i,:] = MonthlyQ_h[i*12:(i+1)*12,-1]/np.sum(MonthlyQ_h[i*12:(i+1)*12,-1])


#Disaggregate flows to monthly based on nearest neighbor
dists = np.zeros([nYears,np.shape(AnnualQ_h)[0]]) 
for j in range(nYears):
    for m in range(np.shape(AnnualQ_h)[0]):
        dists[j,m] = dists[j,m] + (transformedflows[j] - AnnualQ_h[m,-1])**2
                    
        probs = np.zeros([int(np.sqrt(np.shape(AnnualQ_h)[0]))])
        for j in range(len(probs)):
            probs[j] = 1/(j+1)
            
        probs = probs / np.sum(probs)
        for j in range(len(probs)-1):
            probs[j+1] = probs[j] + probs[j+1]
            
    
probs = np.insert(probs, 0, 0)   
MonthlyQ_s = np.zeros([nYears,12])

for j in range(nYears):
    # select one of k nearest neighbors for each simulated year
    neighbors = np.sort(dists[j])[0:int(np.sqrt(np.shape(AnnualQ_h)[0]))]
    indices = np.argsort(dists[j])[0:int(np.sqrt(np.shape(AnnualQ_h)[0]))]
    randnum = random()
    for k in range(1,len(probs)):
        if randnum > probs[k-1] and randnum <= probs[k]:
            neighbor_index = indices[k-1]
   
    # use selected neighbors to downscale flows and demands each year at last node, accounting for time shift of peak
    proportions = LastNodeFractions[neighbor_index,:]
    MonthlyQ_s[j,:] = proportions*transformedflows[j]
    
    
    
    
    
x = np.arange(12)
x_labels = ['O','N','D','J','F','M','A','M','J','J','A','S']

for a in range (10000):
    plt.plot(x, MonthlyQ_s[a,:],color="gray")
    plt.xticks(x, x_labels)
for a in range (105):
    plt.plot(x, W[a,:],color="black") 
    plt.xticks(x, x_labels)
    plt.xlabel("Month")
    plt.ylabel("Flow at last node (af)")
plt.savefig("Gunnison.png",dpi=200,bbox_inches="tight")    



###########################################################
import numpy as np; np.random.seed(42)
import matplotlib.pyplot as plt

#data0 = np.random.rayleigh(10,144)
#data1 = np.random.rayleigh(9,144)
#data2 = np.random.normal(10,5,144)

#data = np.c_[data0, data1, data2]




exceedence = np.arange(1.,len(MonthlyQ_s)+1) /len(MonthlyQ_s)
sort = np.sort(MonthlyQ_s, axis=0)[::-1]

plt.fill_between(exceedence*100, np.min(sort, axis=1),np.max(sort, axis=1),color='gray')

plt.xlabel("Exceedence [%]")
plt.ylabel("Flow at Last Node (af)")
plt.yscale("log")
#plt.grid()
exceedence = np.arange(1.,len(W)+1) /len(W)
sort = np.sort(W, axis=0)[::-1]

plt.fill_between(exceedence*100, np.min(sort, axis=1),np.max(sort, axis=1),color='black')
plt.savefig("Gunnison_FDC.png",dpi=200,bbox_inches="tight")    

plt.show()