# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 16:38:33 2019

@author: Raoul
"""
from astropy import units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun, Angle
from astropy.time import Time

###Disable the IERS download
from astropy.utils import iers
iers.conf.auto_download = False

###Set the location on earth and time of the observation
loc = EarthLocation(lat='49d47m38s', lon='9d47m45', height=305*u.m)


###Convert Ra, Dec to Az, El
def convertEqToAz(ra, dec):
    obj = SkyCoord(ra=ra, dec=dec, frame="icrs")
    
    newCoords = obj.transform_to(AltAz(location=loc, obstime=Time.now()))
    coordinates = newCoords.to_string('decimal').split()
    
    az = coordinates[0]
    el = coordinates[1]
    
    return float(az), float(el)


###Convert Az, El to Ra, Dec
def convertAzToEq(az, el, obsTime):
    obj = SkyCoord(az=az*u.degree, 
                   alt=el*u.degree, 
                   frame=AltAz(location=loc, obstime=obsTime))
    
    newCoords = obj.transform_to("icrs")
    coordinates = newCoords.to_string('decimal').split()
    
    ra = coordinates[0]
    dec = coordinates[1]
    
    return ra, dec


###Calculate the current coordinates for an object that was at the 
###time start_time at the position start_pos
def calculate_new_coordinates(start_pos, start_time):
    obj = SkyCoord(az=start_pos[0]*u.degree, 
                   alt=start_pos[1]*u.degree, 
                   frame=AltAz(location=loc, obstime=start_time))
    
    newCoords = obj.transform_to(AltAz(location=loc, obstime=Time.now()))
    coordinates = newCoords.to_string('decimal').split()
    
    az = coordinates[0]
    el = coordinates[1]
    
    return az, el