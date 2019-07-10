# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 16:08:21 2019

@author: Roman
"""

filename = "azimut"
i = 0

f = open(filename, "r")


frequencies = "" 
freq = []
cleanFreq = []
lastFreq = ""


amplitudes = "" 
lastAmp = ""
cleanAmps = []
SigAmps=[]

for line in f:
    print(i,line)
    i+=1


print(cleanFreq)