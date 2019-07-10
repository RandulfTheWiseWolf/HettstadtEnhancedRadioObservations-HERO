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


a4=AZ.groupby('Grad').mean().reset_index()
e4=EL.groupby('Grad').mean().reset_index()


a5=AZ.groupby('Grad').median().reset_index()
e5=EL.groupby('Grad').median().reset_index()
#print(a5)


plt.figure()
plt.plot(a1['Grad'],a1['Amplitude'], label='1.370666')
plt.plot(a2['Grad'],a2['Amplitude'], label='1.420416')
plt.plot(a3['Grad'],a3['Amplitude'], label='1.469168')
plt.legend()
plt.show()

plt.figure()
plt.plot(e1['Grad'],e1['Amplitude'], label='1.370666')
plt.plot(e2['Grad'],e2['Amplitude'], label='1.420416')
plt.plot(e3['Grad'],e3['Amplitude'], label='1.469168')
plt.legend()
plt.show()

####UFO Data

AZU=pd.read_csv('Azimut-UFO-Werte')
ELU=pd.read_csv('Elevation-UFO-Werte')

au4=AZU.groupby('Grad').mean().reset_index()
eu4=ELU.groupby('Grad').mean().reset_index()

au5=AZU.groupby('Grad').median().reset_index()
eu5=ELU.groupby('Grad').median().reset_index()

#print(au4)
au1=AZU.loc[AZU['Frequenz']==1.152466]
eu1=ELU.loc[ELU['Frequenz']==1.152466]
au2=AZU.loc[AZU['Frequenz']==1.189970]
eu2=ELU.loc[ELU['Frequenz']==1.189970]
au3=AZU.loc[AZU['Frequenz']==1.221185]
eu3=ELU.loc[ELU['Frequenz']==1.221185]

plt.figure()
plt.plot(au1['Grad'],au1['Amplitude'], label='1.152466')
plt.plot(au2['Grad'],au2['Amplitude'], label='1.189970')
plt.plot(au3['Grad'],au3['Amplitude'], label='1.221185')
plt.legend()
plt.show()

plt.figure()
plt.plot(eu1['Grad'],eu1['Amplitude'], label='1.152466')
plt.plot(eu2['Grad'],eu2['Amplitude'], label='1.189970')
plt.plot(eu3['Grad'],eu3['Amplitude'], label='1.221185')
plt.legend()
plt.show()

#mean
plt.figure()
plt.plot(e4['Grad'],e4['Amplitude'], label='el mean')
plt.plot(a4['Grad'],a4['Amplitude'], label='az mean')
plt.plot(e5['Grad'],e5['Amplitude'], label='el median')
plt.plot(a5['Grad'],a5['Amplitude'], label='az median')
plt.legend()
plt.savefig('Crosscan Sonne')

plt.show()

plt.figure()
plt.plot(eu4['Grad'],eu4['Amplitude'], label='ufo el')
plt.plot(au4['Grad'],au4['Amplitude'], label='ufo az')
plt.plot(eu5['Grad'],eu5['Amplitude'], label='el ufo median')
plt.plot(au5['Grad'],au5['Amplitude'], label='az ufo median')
plt.legend()
plt.savefig('Ufo Crossscan')
plt.show()


from mpl_toolkits.mplot3d import Axes3D#
fig = plt.figure()
ax = fig.gca(projection='3d')

az2=AZ.loc[AZ['Frequenz']>0]

ax.plot(xs=az2['Grad'],ys=az2['Frequenz'],zs=az2['Amplitude'])
plt.show()
