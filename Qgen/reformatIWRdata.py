def writeNewFiles(filename, firstLine, numSites):
    # split data on periods
    with open(filename,'r') as f:
        all_split_data = [x.split('.') for x in f.readlines()]
        
    f.close()
    
    numYears = int((len(all_split_data)-firstLine)/numSites)
    MonthlyIWR = np.zeros([12*numYears,numSites])
    for i in range(numYears):
        for j in range(numSites):
            index = firstLine + i*numSites + j
            all_split_data[index][0] = all_split_data[index][0].split()[2]
            MonthlyIWR[i*12:(i+1)*12,j] = np.asfarray(all_split_data[index][0:12], float)
            
    np.savetxt('MonthlyIWR_'+name+'.csv',MonthlyIWR,fmt='%d',delimiter=',')
    
    # calculate annual flows
    AnnualIWR = np.zeros([numYears,numSites])
    for i in range(numYears):
        AnnualIWR[i,:] = np.sum(MonthlyIWR[i*12:(i+1)*12],0)
        
    np.savetxt('AnnualIWR_'+name+'.csv',AnnualIWR,fmt='%d',delimiter=',')
            
    return None

writeNewFiles('D:/Documents/UCRB_analysis-master/Data/'+name+'/'+abbrev+'2015_StateMod_modified/StateMod/'+abbrev+'2015B.iwr', startIWR, nIWRSites)


#writeNewFiles('cm2015B.iwr', 463, 379)
#writeNewFiles('D:/Documents/ym2015_StateMod_modified/ym2015_StateMod_modified/StateMod/ym2015B.iwr', 370, 298)
#writeNewFiles('D:/Documents/gm2015_StateMod_modified/gm2015_StateMod_modified/StateMod/gm2015B.iwr', 620, 550)