# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 13:49:07 2019

@author: Roman
"""
import pandas as pd
import matplotlib.pyplot as plt



######SUN Data

AZ=pd.read_csv('Azimut-Werte')
EL=pd.read_csv('Elevation-Werte')


a1=AZ.loc[AZ['Frequenz']==1.370666]
e1=EL.loc[EL['Frequenz']==1.370666]
a2=AZ.loc[AZ['Frequenz']==1.420416]
e2=EL.loc[EL['Frequenz']==1.420416]
a3=AZ.loc[AZ['Frequenz']==1.469168]
e3=EL.loc[EL['Frequenz']==1.469168]


a4=AZ.groupby('Zeit(s)').mean().reset_index()
e4=EL.groupby('Zeit(s)').mean().reset_index()


a5=AZ.groupby('Zeit(s)').median().reset_index()
e5=EL.groupby('Zeit(s)').median().reset_index()
print(a5)


plt.figure()
plt.plot(a1['Zeit(s)'],a1['Amplitude'], label='1.370666')
plt.plot(a2['Zeit(s)'],a2['Amplitude'], label='1.420416')
plt.plot(a3['Zeit(s)'],a3['Amplitude'], label='1.469168')
plt.legend()
plt.show()

plt.figure()
plt.plot(e1['Zeit(s)'],e1['Amplitude'], label='1.370666')
plt.plot(e2['Zeit(s)'],e2['Amplitude'], label='1.420416')
plt.plot(e3['Zeit(s)'],e3['Amplitude'], label='1.469168')
plt.legend()
plt.show()

####UFO Data

AZU=pd.read_csv('Azimut-UFO-Werte')
ELU=pd.read_csv('Elevation-UFO-Werte')

au4=AZU.groupby('Zeit(s)').mean().reset_index()
eu4=ELU.groupby('Zeit(s)').mean().reset_index()

au5=AZ.groupby('Zeit(s)').median().reset_index()
eu5=EL.groupby('Zeit(s)').median().reset_index()

#print(au4)
au1=AZU.loc[AZU['Frequenz']==1.152466]
eu1=ELU.loc[ELU['Frequenz']==1.152466]
au2=AZU.loc[AZU['Frequenz']==1.189970]
eu2=ELU.loc[ELU['Frequenz']==1.189970]
au3=AZU.loc[AZU['Frequenz']==1.221185]
eu3=ELU.loc[ELU['Frequenz']==1.221185]

plt.figure()
plt.plot(au1['Zeit(s)'],au1['Amplitude'], label='1.152466')
plt.plot(au2['Zeit(s)'],au2['Amplitude'], label='1.189970')
plt.plot(au3['Zeit(s)'],au3['Amplitude'], label='1.221185')
plt.legend()
plt.show()

plt.figure()
plt.plot(eu1['Zeit(s)'],eu1['Amplitude'], label='1.152466')
plt.plot(eu2['Zeit(s)'],eu2['Amplitude'], label='1.189970')
plt.plot(eu3['Zeit(s)'],eu3['Amplitude'], label='1.221185')
plt.legend()
plt.show()

#mean
plt.figure()
plt.plot(e4['Zeit(s)'],e4['Amplitude'], label='el mean')
plt.plot(a4['Zeit(s)'],a4['Amplitude'], label='az mean')
plt.plot(e5['Zeit(s)'],e5['Amplitude'], label='el median')
plt.plot(a5['Zeit(s)'],a5['Amplitude'], label='az median')
plt.legend()
plt.show()

plt.figure()
plt.plot(eu4['Zeit(s)'],eu4['Amplitude'], label='ufo el')
plt.plot(au4['Zeit(s)'],au4['Amplitude'], label='ufo az')
plt.plot(eu5['Zeit(s)'],eu5['Amplitude'], label='el ufo median')
plt.plot(au5['Zeit(s)'],au5['Amplitude'], label='az ufo median')
plt.legend()
plt.show()


