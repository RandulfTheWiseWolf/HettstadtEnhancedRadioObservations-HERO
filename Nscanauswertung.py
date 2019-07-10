# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 14:43:55 2019

@author: Roman
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np




df=pd.read_csv('NScanWerte')

meanframe=df.groupby('Messung').mean().reset_index()
medianframe=df.groupby('Messung').median().reset_index()


ellist=[]
azlist=[]
#azstart=-10
#elstart=10
for i in range(10, -11, -5):
    for schmi in range(-10, 11, 5):
        ellist.append(i)
        azlist.append(schmi)


print(ellist,azlist)     
meanframe['Az']=azlist
medianframe['Az']=azlist   
meanframe['El']=ellist
medianframe['El']=ellist


minwert=meanframe.loc[meanframe['Amplitude'].idxmin(), 'Amplitude']
#df.loc[df['ywert'].idxmax(), 'ywert']
print(minwert)
abc=np.ones_like(meanframe['Az'])*minwert

meanframe['Amplitude']=meanframe['Amplitude']+abs(minwert)

fig = plt.figure()

ax = fig.add_subplot(111, projection='3d')
ax.bar3d(x=meanframe['Az'], y=meanframe['El'], z=abc, dx=2.5,dz=meanframe['Amplitude'],dy=2.5 , shade=True)
plt.savefig('Mean')
plt.show()


minwert=medianframe.loc[medianframe['Amplitude'].idxmin(), 'Amplitude']
abc=np.ones_like(medianframe['Az'])*minwert
medianframe['Amplitude']=medianframe['Amplitude']+abs(minwert)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.bar3d(x=medianframe['Az'], y=medianframe['El'], z=abc, dx=2.5,dz=medianframe['Amplitude'],dy=2.5 , shade=True)
plt.savefig('Median')
plt.show()









#print(meanframe)
#print(medianframe)