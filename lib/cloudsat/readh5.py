import h5py,datetime
import dateutil.tz as tz
filename='2009197050922_17109_CS_2C-RAIN-PROFILE_GRANULE_P_R04_E02.h5'
f=h5py.File(filename,'r')
var_names=\
    {'longitude':'/2C-RAIN-PROFILE/Geolocation Fields/Longitude'
    'latitude':'/2C-RAIN-PROFILE/Geolocation Fields/Latitude'
    'profile_time':'/2C-RAIN-PROFILE/Geolocation Fields/Profile_time'
    'DEM_elevation':'/2C-RAIN-PROFILE/Geolocation Fields/DEM_elevation'
    'tai_start':'/2C-RAIN-PROFILE/Geolocation Fields/TAI_start'
    'height':'/2C-RAIN-PROFILE/Geolocation Fields/Height'
    'liquid':'/2C-RAIN-PROFILE/Data Fields/precip_liquid_water'
    'rain_rate':'/2C-RAIN-PROFILE/Data Fields/rain_rate'
taiDelta=datetime.timedelta(seconds=tai_start[0][0])
taiDayOne=datetime.datetime(1993,1,1,tzinfo=tz.tzutc())
