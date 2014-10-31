""" modified 2012/11/23 to eliminate need for matlab"""
from mpl_toolkits.basemap import Basemap
import scipy.io
import matplotlib.pyplot as plt
import numpy as np
import pyhdf.SD
#
# read the lat lons from the mat file prepared
# by readgeo.m
#
from readcloudsat import get_geo

radarFile='2008291181813_13156_CS_2B-GEOPROF_GRANULE_P_R04_E02.hdf'
lat,lon,time_vals,time_seconds,dem_elevation=get_geo(radarFile)
fig1=plt.figure(1,figsize=(4,5),dpi=150)
fig1.clf()
#
# plot orbit using the radar ground track
#
axis1 = fig1.add_subplot(111)
lon_mid=0
transform = Basemap(projection='vandg',lon_0=lon_mid,ax=axis1)
transform.drawcoastlines()
# draw parallels and meridians.
transform.drawparallels(np.arange(-60.,90.,30.),labels=[1,0,0,0])
transform.drawmeridians(np.arange(0.,360.,60.),labels=[0,0,0,1],fontsize=12)
x,y=transform(lon,lat)    
#make a red circle for starting point
axis1.plot(x[0],y[0],'ro',markersize=5)
for i in np.arange(1000,len(time_vals),1000):
    #make blue circles every 1000 seconds
    axis1.plot(x[i],y[i],'bo',markersize=5)
    #label each circle with the vector index, left justified
    time_string=time_vals[i].strftime('%H:%M UCT')
    axis1.text(x[i],y[i],"   {0:s}".format(time_string),size=5,ha='left')
axis1.set_title(radarFile,size=6)
fig1.canvas.draw()
fig1.savefig('orbit.png')

plt.show()



                      
