""" modified 2012/11/24 to add cast for LayerTop"""
import matplotlib
import datetime
import dateutil.tz as tz
import numpy as np
import matplotlib.pyplot as plt
import h5py


def convert_field(void_field):
    """
      convert a numpy array of tuples
      into a regular numpy array of the same
      shape and dtype
    """
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
        date_time=orbitStart + datetime.timedelta(seconds=float(the_time))
        time_vals.append(date_time)
    var_dict['date_day']=time_vals
    neg_values=var_dict['DEM_elevation'] < 0
    var_dict['DEM_elevation'][neg_values]=0
    #
    # return a list with the five variables
    #
    variable_names=['Latitude','Longitude','date_day','Profile_time','DEM_elevation']
    out_list=[var_dict[varname] for varname in variable_names]
    return out_list

if __name__=="__main__":
    #this flag makes sure the data file can't be overwritten
    #radar reflectivity data see
    #http://www.cloudsat.cira.colostate.edu/dataSpecs.php?prodid=9
    radar_file='2010247105814_23156_CS_2B-GEOPROF_GRANULE_P_R04_E03.h5'
    lat,lon,date_day,prof_seconds,dem_elevation=get_geo(radar_file)
    lidar_file='2010247105814_23156_CS_2B-GEOPROF-LIDAR_GRANULE_P2_R04_E03.h5'
    ## #
    ## # height values stored as an SD dataset
    ## #
    with h5py.File(radar_file,'r') as f:
        height=f['2B-GEOPROF']['Geolocation Fields']['Height'].value
        height=height.astype(np.float)
        refl_vals=f['2B-GEOPROF']['Data Fields']['Radar_Reflectivity'].value
        refl_vals=refl_vals.astype(np.float)
        refl_scale=(f['2B-GEOPROF']['Swath Attributes']['Radar_Reflectivity.factor'].value)[0][0]
        refl_vals=refl_vals/refl_scale
    with h5py.File(lidar_file,'r') as f:
        layerTop=f['2B-GEOPROF-LIDAR/Data Fields/LayerTop'].value
        layerTop=layerTop.astype(np.float)
        layerTop[layerTop < 0]=np.nan

    plt.close('all')
    fig1=plt.figure(1)
    fig1.clf()
    axis1=fig1.add_subplot(1,1,1)
    start=21000
    stop=22000
    start=5000
    stop=6000
    #
    # subset the array
    #
    part_refl=refl_vals[start:stop,:]
    #
    # mask out the uninteresting reflectivities
    #
    hit=np.logical_or(part_refl < -5.,part_refl > 20)
    refl_masked=np.ma.masked_array(part_refl,hit)
    #
    # convert height to km
    #
    im=axis1.pcolormesh(prof_seconds[start:stop],height[0,:]/1.e3,refl_masked.T)
    axis1.set_xlabel('time after orbit start (seconds)')
    axis1.set_ylabel('height (km)')
    start,stop=[item.strftime('%Y-%m-%d %H:%M:%S') for item in (date_day[start],date_day[stop])]
    axis1.set_title('{} to {}'.format(start,stop))
    axis1.set_ylim([0,10])
    cb=fig1.colorbar(im)
    cb.set_label('reflectivity (dbZ)')
    fig1.savefig('reflectivity.png')

    
    fig2=plt.figure(2)
    axis2=fig2.add_subplot(1,1,1)
    axis2.plot(prof_seconds,layerTop[:,0]/1.e3,'b')
    axis2.plot(prof_seconds,dem_elevation/1.e3,'r')
    axis2.set_xlabel('time after orbit start (seconds)')
    axis2.set_ylabel('height (km)')
    axis2.set_title('lidar cloud top (blue) and dem surface elevation (red)')
    fig2.savefig('lidar_height.png')
    plt.show()

    


