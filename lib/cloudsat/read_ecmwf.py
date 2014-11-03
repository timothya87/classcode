from pyhdf import VS
import pyhdf
import pyhdf.HDF as HDF
import pyhdf.SD
import numpy as np
from readcloudsat import get_geo
import matplotlib.pyplot as plt

if __name__=="__main__":
    ecmwfname='2008291181813_13156_CS_ECMWF-AUX_GRANULE_P_R04_E02.hdf'
    lat,lon,time_utc,prof_seconds,dem_elevation=get_geo(ecmwfname)
    hdffile=HDF.HDF(ecmwfname,HDF.HC.READ)
    vs=hdffile.vstart()
    the_vs_data=vs.attach('EC_height')
    nrecs=the_vs_data._nrecs
    height=the_vs_data.read(nRec=nrecs)
    height=np.array(height).squeeze()
    the_vs_data.detach()
    readonly=pyhdf.SD.SDC.READ
    sdfile=pyhdf.SD.SD(ecmwfname,readonly)
    temp_soundings=sdfile.select('Temperature')
    temp_array=temp_soundings.get()
    sdfile.end()
    start=20000
    stop=22000
    temp_array=temp_array[start:stop,:]
    temp_avg=temp_array.mean(axis=0)
    fig1=plt.figure(1)
    fig1.clf()
    axis1=fig1.add_subplot(1,1,1)
    axis1.plot(temp_avg,height/1.e3)
    axis1.set_ylim([0,25])
    axis1.set_xlim([180,300])
    axis1.set_xlabel('temperature (K)')
    axis1.set_ylabel('height (km)')
    axis1.set_title('ecmwf sounding for orbit 13156 from 2008-291: 19:12 to 19:16 UTC')
    fig1.canvas.draw()
    fig1.savefig('sounding.png')
    plt.show()

