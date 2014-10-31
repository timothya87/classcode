""" modified 2012/11/23 to eliminate need for matlab"""
import matplotlib
import datetime
import dateutil.tz as tz
import numpy as np
import matplotlib.dates as mpldates 
import matplotlib.pyplot as plt
import pyhdf.SD
from pyhdf import VS
import pyhdf
import pyhdf.HDF as HDF
import sys
from readcloudsat import get_geo

if __name__=="__main__":
    #this flag makes sure the data file can't be overwritten
    readonly=pyhdf.SD.SDC.READ
    #http://www.cloudsat.cira.colostate.edu/dataSpecs.php?prodid=9
    rainfilename='2008291181813_13156_CS_2C-RAIN-PROFILE_GRANULE_P_R04_E02.hdf'
    rainfilename='2009197050922_17109_CS_2C-RAIN-PROFILE_GRANULE_P_R04_E02.hdf'
    lat,lon,time_utc,prof_seconds,dem_elevation=get_geo(rainfilename)
    hdffile=HDF.HDF(rainfilename,HDF.HC.READ)
    vs=hdffile.vstart()
    rain_rate_vs=vs.attach('rain_rate')
    nrecs=rain_rate_vs._nrecs
    rain_rate=rain_rate_vs.read(nRec=nrecs)
    rain_rate=np.array(rain_rate)
    rain_rate[rain_rate < 0]=np.nan
        
    fig1=plt.figure(1)
    fig1.clf()
    axis1=fig1.add_subplot(1,1,1)
    axis1.plot(rain_rate)
    axis1.set_xlabel('index value')
    axis1.set_ylabel('rain rate (mm/hour)')
    axis1.set_title('rain rate for all values')
    fig1.savefig('rain1.png')
    
    fig2=plt.figure(2)
    fig2.clf()
    axis2=fig2.add_subplot(1,1,1)
    start=20000
    stop=22000
    axis2.plot(rain_rate[start:stop])
    axis2.set_xlabel('index value')
    axis2.set_ylabel('rain rate (mm/hour)')
    axis2.set_title('rain rate for 2000 values')
    fig2.savefig('rain2.png')

    #
    # use matplotlib's date formatter to format the xaxis in
    # mm:ss utc
    #
    fig3=plt.figure(3)
    fig3.clf()
    axis3=fig3.add_subplot(1,1,1)
    formatter = mpldates.DateFormatter('%H:%M')
    axis3.xaxis.set_major_formatter(formatter)
    axis3.plot(time_utc[start:stop],rain_rate[start:stop])
    axis3.set_xlabel('time (UTC)')
    axis3.set_ylabel('rain rate (mm/hour)')
    fig3.savefig('rain3.png')
    plt.show()

     
