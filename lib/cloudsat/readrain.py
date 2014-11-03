""" modified 2012/11/23 to eliminate need for matlab"""
import matplotlib
import datetime
import dateutil.tz as tz
import numpy as np
import matplotlib.dates as mpldates 
import matplotlib.pyplot as plt
import h5py
import sys
from readcloudsat import get_geo,convert_field

if __name__=="__main__":
    #http://www.cloudsat.cira.colostate.edu/dataSpecs.php?prodid=9
    rainfilename='2010247105814_23156_CS_2C-RAIN-PROFILE_GRANULE_P_R04_E03.h5'
    rainfilename='2009197050922_17109_CS_2C-RAIN-PROFILE_GRANULE_P_R04_E02.h5'
    lat,lon,time_utc,prof_seconds,dem_elevation=get_geo(rainfilename)
    with h5py.File(rainfilename,'r') as f:
        rain_rate=f['2C-RAIN-PROFILE']['Data Fields']['rain_rate'].value
        rain_rate=[item[0] for item in rain_rate]
        rain_rate=np.array(rain_rate)
    #rain_rate[rain_rate < -9000]=np.nan
    plt.close('all')
    plt.hist(rain_rate)
    plt.show()    
    ## fig1=plt.figure(1)
    ## fig1.clf()
    ## axis1=fig1.add_subplot(1,1,1)
    ## axis1.plot(rain_rate)
    ## axis1.set_xlabel('index value')
    ## axis1.set_ylabel('rain rate (mm/hour)')
    ## axis1.set_title('rain rate for all values')
    ## fig1.savefig('rain1.png')
    
    ## fig2=plt.figure(2)
    ## fig2.clf()
    ## axis2=fig2.add_subplot(1,1,1)
    ## start=20000
    ## stop=22000
    ## axis2.plot(rain_rate[start:stop])
    ## axis2.set_xlabel('index value')
    ## axis2.set_ylabel('rain rate (mm/hour)')
    ## axis2.set_title('rain rate for 2000 values')
    ## fig2.savefig('rain2.png')

    ## #
    ## # use matplotlib's date formatter to format the xaxis in
    ## # mm:ss utc
    ## #
    ## fig3=plt.figure(3)
    ## fig3.clf()
    ## axis3=fig3.add_subplot(1,1,1)
    ## formatter = mpldates.DateFormatter('%H:%M')
    ## axis3.xaxis.set_major_formatter(formatter)
    ## axis3.plot(time_utc[start:stop],rain_rate[start:stop])
    ## axis3.set_xlabel('time (UTC)')
    ## axis3.set_ylabel('rain rate (mm/hour)')
    ## fig3.savefig('rain3.png')
    ## plt.show()

     
