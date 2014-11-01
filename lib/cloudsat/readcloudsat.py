""" modified 2012/11/24 to add cast for LayerTop"""
import matplotlib
import datetime
import dateutil.tz as tz
import numpy as np
import matplotlib.pyplot as plt
import h5py
from netCDF4 import Dataset
import pyhdf.SD
from pyhdf import VS
import pyhdf
import pyhdf.HDF as HDF

def convert_field(void_field):
    save_shape=void_field.shape
    flat_test=void_field.flat
    out_flat=np.empty(len(flat_test),dtype=flat_test[0][0].dtype)
    for index,item in enumerate(flat_test):
        out_flat[index]=item[0]
    out=out_flat.reshape(save_shape)
    return out

def get_geo(hdfname):
    """given the name of any hdf file from the Cloudsat data archive
       return lat,lon,time_vals,prof_times,dem_elevation
       for the cloudsat orbital swath
       usage:  lat,lon,height,time_vals,prof_times,dem_elevation=get_geo(hdffile)
       parameters:
         input:
           hdfname:  string with name of hdf file from http://www.cloudsat.cira.colostate.edu/dataSpecs.php
         output:  
           lat  -- profile latitude in degrees east  (1-D vector)
           lon  -- profile longitude in degrees north (1-D vector)
           time_vals -- profile times in UTC  (1D vector)
           prof_times -- profile times in seconds since beginning of orbit (1D vector)
           dem_elevation -- surface elevation in meters
    """
    
    with h5py.File(hdfname,'r') as f:
        root_name=f.keys()[0]
        print('reading h5 dataset {} root: {}'.format(hdfname,root_name))
        variable_names=['Longitude','Latitude','Profile_time','DEM_elevation']
        var_dict={}
        for var_name in variable_names:
            var_dict[var_name]=convert_field(f[root_name]['Geolocation Fields'][var_name][...])
        tai_start=f[root_name]['Geolocation Fields']['TAI_start'][0][0]
    #tai_start is the number of seconds since Jan 1, 1993 that the orbit
    #began
    taiDelta=datetime.timedelta(seconds=tai_start)
    taiDayOne=datetime.datetime(1993,1,1,tzinfo=tz.tzutc())
    #this is the start time of the orbit in seconds since Jan 1, 1993
    orbitStart=taiDayOne + taiDelta
    time_vals=[]
    #now loop throught he radar profile times and convert them to 
    #python datetime objects in utc
    for the_time in var_dict['Profile_time']:
        time_vals.append(orbitStart + datetime.timedelta(seconds=float(the_time)))
    var_dict['time_vals']=time_vals
    neg_values=var_dict['DEM_elevation'] < 0
    var_dict['DEM_elevation'][neg_values]=0
    return var_dict

if __name__=="__main__":
    #this flag makes sure the data file can't be overwritten
    #radar reflectivity data see
    #http://www.cloudsat.cira.colostate.edu/dataSpecs.php?prodid=9
    radar_file='2010247105814_23156_CS_2B-GEOPROF_GRANULE_P_R04_E03.h5'
    geo_vars_radar=get_geo(radar_file)
    lidar_file='2010247105814_23156_CS_2B-GEOPROF-LIDAR_GRANULE_P2_R04_E03.h5'
    geo_vars_lidar=get_geo(lidar_file)
    radar_file='2009197050922_17109_CS_2C-RAIN-PROFILE_GRANULE_P_R04_E02.h5'
    geo_vars_radar=get_geo(radar_file)
    test=Dataset('2009197050922_17109_CS_2C-RAIN-PROFILE_GRANULE_P_R04_E02.nc')
    hdfname='2009197050922_17109_CS_2C-RAIN-PROFILE_GRANULE_P_R04_E02.hdf'
    hdffile=HDF.HDF(hdfname,HDF.HC.READ)
    var_name='Latitude'
    vs=hdffile.vstart()
    the_var=vs.attach(var_name)
    nrecs=the_var._nrecs
    the_data=the_var.read(nRec=nrecs)
    the_data=np.array(the_data).squeeze()
    var_name='Longitude'
    vs=hdffile.vstart()
    the_var=vs.attach(var_name)
    nrecs=the_var._nrecs
    the_data=the_var.read(nRec=nrecs)
    the_data=np.array(the_data).squeeze()

    ## #
    ## # height values stored as an SD dataset
    ## #
    ## hdf_SD=pyhdf.SD.SD(radar_file,readonly)
    ## height_sd=hdf_SD.select('Height')
    ## height_vals=height_sd.get()
    ## height=height_vals.astype(np.float)
    ## refl=hdf_SD.select('Radar_Reflectivity')
    ## refl_vals=refl.get()
    ## scale_factor=refl.attributes()['factor']
    ## hdf_SD.end()
    ## #print refl.attributes()
    ## refl_vals=refl_vals/scale_factor
    ## lidar_file='2008291181813_13156_CS_2B-GEOPROF-LIDAR_GRANULE_P1_R04_E02.hdf'
    ## lidar_file='2010247105814_23156_CS_2B-GEOPROF-LIDAR_GRANULE_P2_R04_E03.hdf'
    ## lidar_data=pyhdf.SD.SD(lidar_file,readonly)
    ## layerTop=lidar_data.select('LayerTop')
    ## layerTop=layerTop.get()
    ## layerTop=layerTop.astype(np.float)
    ## layerTop[layerTop < 0]=np.nan
    
    ## fig1=plt.figure(1)
    ## fig1.clf()
    ## axis1=fig1.add_subplot(1,1,1)
    ## start=21000
    ## stop=22000
    ## start=5000
    ## stop=6000
    ## #
    ## # subset the array
    ## #
    ## part_refl=refl_vals[start:stop,:]
    ## #
    ## # mask out the uninteresting reflectivities
    ## #
    ## hit=np.logical_or(part_refl < -5.,part_refl > 20)
    ## refl_masked=np.ma.masked_array(part_refl,hit)
    ## im=axis1.pcolor(prof_seconds[start:stop],height[0,:]/1.e3,refl_masked.T)
    ## axis1.set_xlabel('time after orbit start (seconds)')
    ## axis1.set_ylabel('height (km)')
    ## axis1.set_ylim([0,10])
    ## cb=fig1.colorbar(im)
    ## cb.set_label('reflectivity (dbZ)')
    ## fig1.savefig('reflectivity.png')
    
    ## fig2=plt.figure(2)
    ## axis2=fig2.add_subplot(1,1,1)
    ## axis2.plot(prof_seconds,layerTop[:,0]/1.e3,'b')
    ## axis2.plot(prof_seconds,dem_elevation/1.e3,'r')
    ## axis2.set_xlabel('time after orbit start (seconds)')
    ## axis2.set_ylabel('height (km)')
    ## axis2.set_title('lidar cloud top (blue) and dem surface elevation (red)')
    ## fig2.savefig('lidar_height.png')
    ## plt.show()

    


