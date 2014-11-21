""" modified 2012/11/24 to add cast for LayerTop
    modified 2014/11/07 
                        temporally remove "__main__"
                        add I/O for radar file
                        add I/O for lidar file
                        combine readrain.py
                        combine read_ecmwf.py
    modified 2014/11/08 rename as cloudsat_tool
                        add monotonic option in get_geo
                        fix bugs                    
 """

import datetime
import dateutil.tz as tz
import numpy as np
import h5py
## used only in __main__
# import matplotlib.pyplot as plt


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

def get_geo(hdfname, monotonic_id=1):
    """given the name of any hdf file from the Cloudsat data archive
       return lat,lon,time_vals,prof_times,dem_elevation
       for the cloudsat orbital swath
       usage:  lat,lon,height,time_vals,prof_times,dem_elevation=get_geo(hdffile)
       parameters:
         input:
           hdfname:  string with name of hdf file from http://www.cloudsat.cira.colostate.edu/dataSpecs.php
           monotonic_id: make the longitude monotonic (=1) or not (~=1)
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
    #
    # <-------- Added on 2014/11/08
    #
    # ===================================================================== #
    if monotonic_id==1:
        lon=var_dict['Longitude'][:];
        for id in range(0, len(lon)-1):
            if lon[id+1] > lon[id]:
                lon[id+1] = lon[id+1]-360
        lonmin=np.amin(lon)
        #
        # basemap requires lons in the range -360 - 720 degrees
        #
        if lonmin < -360.:
            lon[:]=lon[:] + 360.
        var_dict['Longitude']=lon
    # ===================================================================== #
    #
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

def read_radar(hdfname, maskid=1):
    """
    ======================================================================
    I/O functions for CloudSat. 2B-GEOPROF radar file
    ----------------------------------------------------------------------
    height, reflect = read_radar(hdfname)
    ----------------------------------------------------------------------
    Input:
            hdfname: filename
            maskid: do not mask (=0), mask as np.nan (=1),
                    mask as np.mask class (=2) for bad values.
    Output:
            reflect: radar reflectance, dbZ
            height: height, km
    ======================================================================
    """
    obj=h5py.File(hdfname, 'r')
    height=obj['2B-GEOPROF']['Geolocation Fields']['Height'].value.astype(np.float)
    height=height/1e3
    reflect=obj['2B-GEOPROF']['Data Fields']['Radar_Reflectivity'].value.astype(np.float)
    ref_scale=(obj['2B-GEOPROF']['Swath Attributes']['Radar_Reflectivity.factor'].value)[0][0]
    ref_offset=(obj['2B-GEOPROF']['Swath Attributes']['Radar_Reflectivity.offset'].value)[0][0]
    reflect=(reflect-ref_offset)/ref_scale
    ref_id=np.logical_or(reflect < -5, reflect > 20)    
    if maskid==1:
        reflect[ref_id]=np.nan
    if maskid==2:
        reflect=np.ma.masked_where(ref_id, reflect)
    return height, reflect  
    
def read_lidar(hdfname, maskid=1):
    """
    ======================================================================
    I/O functions for CloudSat. 2B-GEOPROF-LIDAR_GRANULE lidar file
    ----------------------------------------------------------------------
    CFrac, LayerTop, LayerBase = read_lidar(hdfname)
    ----------------------------------------------------------------------
    Input:
            hdfname: filename
            maskid: do not mask (=0), mask as np.nan (=1),
                    mask as np.mask class (=2) for bad values.
    Output:
            CFrac: cloud fraction, %
            LayerTop: lider cloud top height, km
            LayerBase: lider cloud base height, km
    ======================================================================
    """
    obj=h5py.File(hdfname, 'r')
    layerTop=obj['2B-GEOPROF-LIDAR/Data Fields/LayerTop'].value.astype(np.float)
    layerBase=obj['2B-GEOPROF-LIDAR/Data Fields/LayerBase'].value.astype(np.float)
    CFrac=obj['2B-GEOPROF-LIDAR/Data Fields/CloudFraction'].value.astype(np.float)
    layerTop=layerTop/1e3
    layerBase=layerBase/1e3
    if maskid == 1:
        layerTop[layerTop < 0]=np.nan
        layerTop[layerBase < 0]=np.nan
        CFrac[CFrac < 0]=np.nan
    if maskid == 2:
        layerTop=np.ma.masked_where(layerTop == 0, layerTop)
        layerBase=np.ma.masked_where(layerBase < 0, layerBase)
        CFrac=np.ma.masked_where(CFrac < 0, CFrac)
    return CFrac, layerTop, layerBase   

def read_ecmwf(hdfname, maskid=1):
    """
    ======================================================================
    I/O functions for CloudSat. ECMWF-AUX file
    ----------------------------------------------------------------------
    P, SLP, T, T2m, SKT, q, O3 = read_ecmwf(hdfname)
    ----------------------------------------------------------------------
    Input:
            hdfname: filename
            maskid: do not mask (=0), mask as np.nan (=1),
                    mask as np.mask class (=2) for bad values.
    Output:
            P: Pressure, hPa, 2-D array
            SLP: Sea level pressure, 
            T: Temperature, degC, 2-D array
            T2m: Temperature on 2m above surface, degC, 1-D array
            SKT: Surface Skin Temperature, degC, 1-D array
            q: Specific Humidity, kg/kg, 2-D array
            O3: Ozone mixing ratio, kg/kg, 2-D array
    ======================================================================
    """
    obj=h5py.File(hdfname, 'r')
    P=obj['ECMWF-AUX/Data Fields/Pressure'].value.astype(np.float); P=P/1e2
    SLP=obj['ECMWF-AUX/Data Fields/Surface_pressure'].value.astype(np.float); SLP=SLP/1e2
    T=obj['ECMWF-AUX/Data Fields/Temperature'].value.astype(np.float); T=T-273.16*np.ones(T.shape)
    T2m=obj['ECMWF-AUX/Data Fields/Temperature_2m'].value.astype(np.float); T2m=T2m-273.16*np.ones(T2m.shape)
    SKT=obj['ECMWF-AUX/Data Fields/Skin_temperature'].value.astype(np.float); SKT=SKT-273.16*np.ones(SKT.shape)
    q=obj['ECMWF-AUX/Data Fields/Specific_humidity'].value.astype(np.float);
    O3=obj['ECMWF-AUX/Data Fields/Ozone'].value;
    if maskid == 1:
        P[P < 0]=np.nan
        SLP[SLP < 0]=np.nan
        T[T < 0]=np.nan
        T2m[T2m < 0]=np.nan
        SKT[SKT < 0]=np.nan
        q[q < 0]=np.nan
        O3[O3 < 0]=np.nan
    if maskid == 2:
        P=np.ma.masked_where(P < 0, P)
        SLP=np.ma.masked_where(SLP < 0, SLP)
        T=np.ma.masked_where(T < 0, T)
        T2m=np.ma.masked_where(T2m < 0, T2m)
        SKT=np.ma.masked_where(SKT < 0, SKT)
        q=np.ma.masked_where(q < 0, q)
        O3=np.ma.masked_where(O3 < 0, O3)
    return P, SLP, T, T2m, SKT, q, O3
    
def read_rain(hdfname, maskid=1):
    """
    ======================================================================
    I/O functions for CloudSat. CS_2C-RAIN-PROFILE file
    ----------------------------------------------------------------------
    rain, precli, precice, clw = read_ecmwf(hdfname)
    ----------------------------------------------------------------------
    Input:
            hdfname: filename
            maskid: do not mask (=0), mask as np.nan (=1),
                    mask as np.mask class (=2) for bad values.
    Output:
            rain: Rain rate, mm/hr, 2-D array
            precli: Liquid precipitation water content, g/m^3, 2-D array
            precice: Ice precipitation water content, g/m^3, 2-D array 
            clw: Cloud liquid water content, degC, g/m^3 2-D array
    ======================================================================
    """
    obj=h5py.File(hdfname, 'r')
    rainRAW=obj['2C-RAIN-PROFILE/Data Fields/rain_rate'].value.astype(np.float)
    rain_factor=obj['2C-RAIN-PROFILE/Data Fields/rain_rate'].attrs.values()[0]
    rain=rainRAW*rain_factor
    precliRAW=obj['2C-RAIN-PROFILE/Data Fields/precip_liquid_water'].value.astype(np.float)
    precli_factor=obj['2C-RAIN-PROFILE/Data Fields/precip_liquid_water'].attrs.values()[2]
    precli=precliRAW*precli_factor
    preciceRAW=obj['2C-RAIN-PROFILE/Data Fields/precip_ice_water'].value.astype(np.float)
    precice_factor=obj['2C-RAIN-PROFILE/Data Fields/precip_ice_water'].attrs.values()[2]
    precice=precliRAW*precli_factor
    clwRAW=obj['2C-RAIN-PROFILE/Data Fields/cloud_liquid_water'].value.astype(np.float)
    clw_factor=obj['2C-RAIN-PROFILE/Data Fields/cloud_liquid_water'].attrs.values()[2]
    clw=clwRAW*clw_factor
    if maskid == 1:
        rain[rainRAW == -9999]=np.nan
        precli[precliRAW == -9999]=np.nan
        precice[preciceRAW == -9999]=np.nan
        clw[clwRAW == -9999]=np.nan
    if maskid == 2:
        rain=np.ma.masked_where(rainRAW == -9999, rain)
        precli=np.ma.masked_where(precliRAW == -9999, precli)
        precice=np.ma.masked_where(preciceRAW == -9999, precice)
        clw=np.ma.masked_where(clwRAW == -9999, clw)
    return rain, precli, precice, clw



    
#if __name__=="__main__":
    #this flag makes sure the data file can't be overwritten
    #radar reflectivity data see
    #http://www.cloudsat.cira.colostate.edu/dataSpecs.php?prodid=9
#    radar_file='2010247105814_23156_CS_2B-GEOPROF_GRANULE_P_R04_E03.h5'
#    lat,lon,date_day,prof_seconds,dem_elevation=get_geo(radar_file)
#    lidar_file='2010247105814_23156_CS_2B-GEOPROF-LIDAR_GRANULE_P2_R04_E03.h5'
    ## #
    ## # height values stored as an SD dataset
    ## #
#    with h5py.File(radar_file,'r') as f:
#        height=f['2B-GEOPROF']['Geolocation Fields']['Height'].value
#        height=height.astype(np.float)
#        refl_vals=f['2B-GEOPROF']['Data Fields']['Radar_Reflectivity'].value
#        refl_vals=refl_vals.astype(np.float)
#        refl_scale=(f['2B-GEOPROF']['Swath Attributes']['Radar_Reflectivity.factor'].value)[0][0]
#        refl_vals=refl_vals/refl_scale
#    with h5py.File(lidar_file,'r') as f:
#        layerTop=f['2B-GEOPROF-LIDAR/Data Fields/LayerTop'].value
#        layerTop=layerTop.astype(np.float)
#        layerTop[layerTop < 0]=np.nan

#    plt.close('all')
#    fig1=plt.figure(1)
#    fig1.clf()
#    axis1=fig1.add_subplot(1,1,1)
#    start=21000
#    stop=22000
#    start=5000
#    stop=6000
    #
    # subset the array
    #
#    part_refl=refl_vals[start:stop,:]
    #
    # mask out the uninteresting reflectivities
    #
#    hit=np.logical_or(part_refl < -5.,part_refl > 20)
#    refl_masked=np.ma.masked_where(part_refl,hit)
    #
    # convert height to km
    #
#    im=axis1.pcolormesh(prof_seconds[start:stop],height[0,:]/1.e3,refl_masked.T)
#    axis1.set_xlabel('time after orbit start (seconds)')
#    axis1.set_ylabel('height (km)')
#    start,stop=[item.strftime('%Y-%m-%d %H:%M:%S') for item in (date_day[start],date_day[stop])]
#    axis1.set_title('{} to {}'.format(start,stop))
#    axis1.set_ylim([0,10])
#    cb=fig1.colorbar(im)
#    cb.set_label('reflectivity (dbZ)')
#   fig1.savefig('reflectivity.png')

    
#    fig2=plt.figure(2)
#    axis2=fig2.add_subplot(1,1,1)
#    axis2.plot(prof_seconds,layerTop[:,0]/1.e3,'b')
#    axis2.plot(prof_seconds,dem_elevation/1.e3,'r')
#    axis2.set_xlabel('time after orbit start (seconds)')
#    axis2.set_ylabel('height (km)')
#    axis2.set_title('lidar cloud top (blue) and dem surface elevation (red)')
#    fig2.savefig('lidar_height.png')
#    plt.show()

    


