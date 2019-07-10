# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 15:57:35 2019

@author: Roman
"""

import pandas as pd

def getTimes(lst):
    relatives = []
    times = []
    
    for l in lst:
        times.append(l[0]*3600 + l[1]*60 + l[2] + l[3]/1000)
    
    for i in range(0, len(times)):
        relatives.append(times[i] - times[0])
        
    return relatives

def cleanseFrequency(line):
        cleanFreq = []
        freq = line.split("\t")
        
        #Everything in units of E+9:
        for fr in freq:
            cleanFreq.append(fr.strip("+E9"))
            
        lastFreq = cleanFreq.pop()
        cleanLastFreq = lastFreq.strip("+E9\r\n")
        cleanFreq.append(cleanLastFreq)
        cleanFreq = cleanFreq[4::]
        
        return cleanFreq
    
def cleanseAmplitude(line):
        
        cleanAmps = line.split("\t")
        
        
        lastAmp = cleanAmps.pop()
        cleanLastAmp = lastAmp.strip("\r\n")
        cleanAmps.append(cleanLastAmp)

        for i in range(0, len(cleanAmps)):
            cleanAmps[i] = float(cleanAmps[i])
        
        return cleanAmps
    

filenames = ["00", "01", "02", "03", "04", "10", "11", "12", "13", "14", "20", "21", "22", "23", "24", "30", "31", "32", "33", "34", "40", "41", "42", "43", "44"]

#savenames = ["Azimut", "Elevation", "Azimut-UFO", "Elevation-UFO"]

filecounter=0

Starts=[]
Ends=[]

dataframes=[]

for filename in filenames:
    i = 0
    f = open(filename, "r")

    sigAmps = []
    


    

    for line in f:
        if i == 6:
            cleanFreq = cleanseFrequency(line)
        
        if i >= 9:
            cleanAmps = cleanseAmplitude(line)
        
            sigAmps.append(cleanAmps)
        
        i += 1 



    for i in range(0, len(cleanFreq)):
        cleanFreq[i] = float(cleanFreq[i])	
        
        
        
    #lastAmp = cleanAmps.pop()
    #cleanLastAmp = lastAmp.strip("\r\n")
    #cleanAmps.append(cleanLastAmp)
    
    #Delete Time
    #cleanAmps = cleanAmps[4::]
    
    
    
    #print(cleanFreq)
    #print(sigAmps)
    
    times = getTimes(sigAmps)
    
    a=0
    for schmist in sigAmps:
        sigAmps[a]=schmist[4:]
        a+=1
            
    #print(times)
            
    #print(len(sigAmps[1]), len(cleanFreq),len(sigAmps))
            
    f.close()
            
    cleanFreqs=cleanFreq*len(times)
    flatAmps=[]
    for i in range(0,len(sigAmps)):
        flatAmps=flatAmps+sigAmps[i]
        
    ttimes=[]
    for time in times:
        for i in range(0,len(sigAmps[0])):
            ttimes.append(time)
                        
    #print(len(ttimes), len(flatAmps),len(cleanFreqs))   
                        
                        
    Daten = {'Frequenz':cleanFreqs,'Amplitude':flatAmps, 'Zeit(s)':ttimes,}
    df = pd.DataFrame(Daten, columns=['Frequenz','Amplitude','Zeit(s)'])
    df['Messung']=filename
    dataframes.append(df)
    #AbsGrad=abs(Ends[filecounter]-Starts[filecounter])
    #df['Grad']=df['Zeit(s)']*AbsGrad/df['Zeit(s)'][len(df['Zeit(s)'])-1]
    
    #print(df['Grad'])
    #finalsavename=savenames[filecounter]+"-Werte"
    #print(df)
    #df.to_csv(finalsavename)
    
    
    filecounter+=1
    #df.to_csv('Elevation-UFO-Werte')
    #df.to_csv('Azimut-UFO-Werte')
    #df.to_csv('Azimut-Werte')
    #df.to_csv('Elevation-Werte')
    #print(df)
df2 = pd.concat(dataframes)
print(df2)   
df2.to_csv('NScanWerte')