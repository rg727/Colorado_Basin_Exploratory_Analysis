# -*- coding: utf-8 -*-
"""
Created on Mon Aug  9 13:25:37 2021

@author: Rohini
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib

#Set these values for each site 
name='Yampa'
abbrev='ym'
startYr=1982
nSites=94

def readFiles(filename, firstLine, numSites):
    # read in all monthly flows and re-organize into nyears x 12 x nsites matrix
    with open(filename,'r') as f:
        all_split_data = [x.split('.') for x in f.readlines()]
        
    f.close()
    
    numYears = int((len(all_split_data)-firstLine)/numSites)
    MonthlyQ = np.zeros([12*numYears,numSites])
    sites = []
    for i in range(numYears):
        for j in range(numSites):
            index = firstLine + i*numSites + j
            sites.append(all_split_data[index][0].split()[1])
            all_split_data[index][0] = all_split_data[index][0].split()[2]
            MonthlyQ[i*12:(i+1)*12,j] = np.asfarray(all_split_data[index][0:12], float)
            
    MonthlyQ = np.reshape(MonthlyQ,[int(np.shape(MonthlyQ)[0]/12),12,numSites])
            
    return MonthlyQ

def revertCumSum(cumulative):
    '''Revert cumulative sum. Modified from https://codereview.stackexchange.com/questions/117183/extracting-original-values-from-cumulative-sum-values'''
    output = [0] * len(cumulative)
    for i,e in reversed(list(enumerate(cumulative))):
        output[i]=cumulative[i] - cumulative[i-1]
    output[0]=cumulative[0]

    return output

# read in monthly flows at all sites
MonthlyQ = readFiles('D:/Documents/UCRB_analysis-master/Data/'+name+'/'+abbrev+'2015_StateMod_modified/StateMod/'+abbrev+'2015x.xbm', 16, nSites)
LastNodeFractions = np.zeros([2013-startYr,61,12])
for i in range(2013-startYr):
    LastNodeFractions[i,0,:] = MonthlyQ[(startYr-1909+1)+i,:,-1]/np.sum(MonthlyQ[(startYr-1909+1)+i,:,-1])

# read in daily flows at last node
LastNodeQ = pd.read_csv('D:/Documents/UCRB_analysis-master/Data/'+name+'/'+name+'_Discharge.csv')
#LastNodeQ = pd.read_csv('CO_River_UT_State_line.csv')
LastNodeQ['Date'] = pd.to_datetime(LastNodeQ['Date'],format="%m/%d/%Y")
LastNodeQ['Year'] = LastNodeQ['Date'].dt.year
LastNodeQ['Month'] = LastNodeQ['Date'].dt.month
# increase year by 1 for Oct->Dec to convert to water year
indices = np.where(LastNodeQ['Month'] >= 10)[0]
LastNodeQ['Year'][indices] += 1

years = np.unique(LastNodeQ['Year'])
for year in years:
    flows = np.where(LastNodeQ['Year']==year)[0]
    plt.plot(range(len(flows)),LastNodeQ['Flow'][flows])
    #plt.savefig('Year' + str(year) + 'Hydrograph.png')
    #plt.clf()
    
# create column of dataframe for shifted flows
LastNodeQ['ShiftedFlow'] = LastNodeQ['Flow']

shifts = range(1,30) # example with 1 mo = 30 days
for shift in shifts:
    LastNodeQ['ShiftedFlow'][0:-shift] = LastNodeQ['Flow'][shift::]
    MonthlyTotals = LastNodeQ.set_index('Date').resample('M').sum()
    MonthlyTotals['Year'] = MonthlyTotals.index.year
    MonthlyTotals['Month'] = MonthlyTotals.index.month
    # reduce year by 1 for Jan->Sept to conver to water year
    indices = np.where(MonthlyTotals['Month'] >= 10)[0]
    MonthlyTotals['Year'][indices] += 1
    # convert Monthly totals from cfs to acre-ft
    MonthlyTotals['Flow'] = MonthlyTotals['Flow'] * 2.29569E-05 * 86400
    MonthlyTotals['ShiftedFlow'] = MonthlyTotals['ShiftedFlow'] * 2.29569E-05 * 86400
    
    for i in range(len(years)-1):
        year = years[i]
        flows = np.where(MonthlyTotals['Year']==year)[0]
        
        # calculate cumulative flows at gage w/ and w/o the shift, and of the naturalized flows
        gage_cdf = np.cumsum(MonthlyTotals['Flow'][flows])
        gage_shifted_cdf = np.cumsum(MonthlyTotals['ShiftedFlow'][flows])
        natural_cdf = np.cumsum(MonthlyQ[7+i,:,-1])
        
        # normalize cdfs to sum to 1
        gage_cdf = gage_cdf/np.max(gage_cdf)
        gage_shifted_cdf = gage_shifted_cdf/np.max(gage_shifted_cdf)
        natural_cdf = natural_cdf/np.max(natural_cdf)
        
        # apply same shift to natural flows as at gage
        natural_shifted_cdf = natural_cdf + gage_shifted_cdf - gage_cdf
        
        # compute monthly fractional contribution
        LastNodeFractions[i,shift,:] = revertCumSum(natural_shifted_cdf)
        
# for each year, make a plot of the base and shifted hydrographs
cmap = matplotlib.cm.get_cmap('coolwarm')
for i in range(len(years)-1):
    plt.plot(MonthlyQ[(startYr-1909+1)+i,:,-1])
    for shift in shifts:
        plt.plot(np.sum(MonthlyQ[(startYr-1909+1)+i,:,-1]) * LastNodeFractions[i,shift,:], c=cmap(shift/30))
        
    #plt.savefig('ShiftedFlows/WY' + str(i+1951) + '.png')
    #plt.clf()
    
# for years 1909-1951, find nearest neighbor in terms of frational contribution and apply same shifts
#LastNodeFractions_preRecord = np.zeros([1952-1909,61,12])
LastNodeFractions_preRecord = np.zeros([startYr+1-1909,61,12])
for i in range(startYr+1-1909):
    d = np.zeros(2013-startYr)
    for j in range(2013-startYr):
        for k in range(12):
            d[j] += (MonthlyQ[i,k,-1]/np.sum(MonthlyQ[i,:,-1]) - MonthlyQ[j+(startYr-1909+1),k,-1]/np.sum(MonthlyQ[j+(startYr-1909+1),:,-1]))**2

    idx = np.argmin(d)
    LastNodeFractions_preRecord[i,:,:] = LastNodeFractions[idx,:,:]
    
# prepend LastNodeFractions_preRecord to MonthlyFraactions
LastNodeFractions = np.concatenate((LastNodeFractions_preRecord,LastNodeFractions),0)

np.save('LastNodeFractions_'+str(name),LastNodeFractions)