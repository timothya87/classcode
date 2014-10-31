""" modified 2012/11/24 to add cast for LayerTop"""
import matplotlib
import datetime
import dateutil.tz as tz
import numpy as np
import matplotlib.pyplot as plt
import h5py

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
    f=h5py.File(filename,'r')
    #uncomment these lines to see the variable names
    #print "SD datasets: ",hdf_SD.datasets()
    #out=vs.vdatainfo()
    #print "VS variable names: ",out
    variable_names=['Longitude','Latitude','Profile_time','DEM_elevation']
    var_dict={}
    for var_name in variable_names:
        the_var=vs.attach(var_name)
        nrecs=the_var._nrecs
        the_data=the_var.read(nRec=nrecs)
        the_data=np.array(the_data).squeeze()
        var_dict[var_name]=the_data
        the_var.detach()
    tai_start=vs.attach('TAI_start')
    nrecs=tai_start._nrecs
    tai_start_value=tai_start.read(nRec=nrecs)
    tai_start.detach()
    hdffile.close()   
    #tai_start is the number of seconds since Jan 1, 1993 that the orbit
    #began
    taiDelta=datetime.timedelta(seconds=tai_start_value[0][0])
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
    variable_names=['Latitude','Longitude','time_vals','Profile_time','DEM_elevation']
    out_list=[var_dict[varname] for varname in variable_names]
    return tuple(out_list)

if __name__=="__main__":
    #this flag makes sure the data file can't be overwritten
    readonly=pyhdf.SD.SDC.READ
    #radar reflectivity data see
    #http://www.cloudsat.cira.colostate.edu/dataSpecs.php?prodid=9
    radar_file='2008291181813_13156_CS_2B-GEOPROF_GRANULE_P_R04_E02.hdf'
    radar_file='2010247105814_23156_CS_2B-GEOPROF_GRANULE_P_R04_E03.hdf'
    lat,lon,time_vals,prof_seconds,dem_elevation=get_geo(radar_file)
    #
    # height values stored as an SD dataset
    #
    hdf_SD=pyhdf.SD.SD(radar_file,readonly)
    height_sd=hdf_SD.select('Height')
    height_vals=height_sd.get()
    height=height_vals.astype(np.float)
    refl=hdf_SD.select('Radar_Reflectivity')
    refl_vals=refl.get()
    scale_factor=refl.attributes()['factor']
    hdf_SD.end()
    #print refl.attributes()
    refl_vals=refl_vals/scale_factor
    lidar_file='2008291181813_13156_CS_2B-GEOPROF-LIDAR_GRANULE_P1_R04_E02.hdf'
    lidar_file='2010247105814_23156_CS_2B-GEOPROF-LIDAR_GRANULE_P2_R04_E03.hdf'
    lidar_data=pyhdf.SD.SD(lidar_file,readonly)
    layerTop=lidar_data.select('LayerTop')
    layerTop=layerTop.get()
    layerTop=layerTop.astype(np.float)
    layerTop[layerTop < 0]=np.nan
    
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
    im=axis1.pcolor(prof_seconds[start:stop],height[0,:]/1.e3,refl_masked.T)
    axis1.set_xlabel('time after orbit start (seconds)')
    axis1.set_ylabel('height (km)')
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

    


