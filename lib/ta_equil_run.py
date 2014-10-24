from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# use pretty plotting if it can be imported
#
try:
    import seaborn
except:
    pass

sigma=5.67e-8

def find_tau(tot_trans,num_layers):
    """
    Finds the optical depth tau given the total trans, and number of layers

    Args:
        tot_trans: (Int)Is the total transmition through the entire layer.
        num_layers: (Int)The number of layers in the atmosphere

    Returns:
        The optical depth at for each level in number of layers given

    """
    trans_layer=tot_trans**(1./num_layers)
    tau_layer= -1.*np.log(trans_layer)
    tau_layers=np.ones([num_layers])*tau_layer
    tau_levels=np.cumsum(tau_layers)
    tau_levels=np.concatenate(([0],tau_levels))
    return tau_levels

def find_heights(press_levels,rho_layers):
    """
    Finds the heights of level given pressure and density of each layer

    Args:
        press_levels: The pressure at each level, a array of values
        rho_layers: The density at each level, an array of values

    Reuturns:
        an array of heights the same legnth as pressure levels and rho_layers

    Raises:
        both press_levels and rho_layers have to be arrays of the same length
    """
    Rd=287.
    g=9.8
    press_layers=(press_levels[1:] + press_levels[:-1])/2.
    del_press=(press_levels[1:] - press_levels[0:-1])
    rho_layers=press_layers/(Rd*Temp_layers)
    del_z= -1.*del_press/(rho_layers*g)
    level_heights=np.cumsum(del_z)
    level_heights=np.concatenate(([0],level_heights))
    return level_heights

def fluxes(tau_levels,Temp_layers,T_surf):
    """
    Returns bot upward radiation and downward radiation, both arrays of the 
    same size

    Args:
        tau_levels: an array of acumulating optical depths from zero
                maximum tau
        Temp_layers: layers of temperatures 
        T_surf: and integer of the Temperature of the surface in Kelvins

    Reuturns:
        an array of upward and downward fluxes of the same size in W/m^2

    Raises: Input arrays must all be of the same size

    """
    up_rad=np.empty_like(tau_levels)
    down_rad=np.empty_like(tau_levels)
    sfc_rad=sigma*T_surf**4.
    up_rad[0]=sfc_rad
    tot_levs=len(tau_levels)
    for index in np.arange(1,tot_levs):
        upper_lev=index
        lower_lev=index - 1
        layer_num=index-1
        del_tau=tau_levels[upper_lev] - tau_levels[lower_lev]
        trans=np.exp(-1.666*del_tau)
        emiss=1 - trans
        layer_rad=sigma*Temp_layers[layer_num]**4.*emiss
        up_rad[upper_lev]=trans*up_rad[lower_lev] + layer_rad
    down_rad[tot_levs-1]=0
    for index in np.arange(1,tot_levs):
        upper_lev=tot_levs - index
        lower_lev=tot_levs - index -1
        layer_num=tot_levs - index - 1
        del_tau=tau_levels[upper_lev] - tau_levels[lower_lev]
        trans=np.exp(-1.666*del_tau)
        emiss=1 - trans
        layer_rad=sigma*Temp_layers[layer_num]**4.*emiss
        down_rad[lower_lev]=down_rad[upper_lev]*trans + layer_rad
    return (up_rad,down_rad)

def heating_rate(net_up,height_levels,rho_layers):
    """
    Retrives the heating rate for each layer in the given atmosphere

    Args:
        net_up: the difference between upward radiation and downward radiation
            with the same size arrays
        height_levels: an array of height levels coorisponing to the net upward radiation
        rho_layers: an array of rho values coorisponding to the same length as net_up

    Returns:
        dT_dt: the heating rate for each layer in the given atmosphere 
    """
    cpd=1004.
    dFn_dz= -1.*np.diff(net_up)/np.diff(height_levels)
    dT_dt=dFn_dz/(rho_layers*cpd)
    return dT_dt

def time_step(heating_rate,Temp_layers,delta_time):
    """
     Retrives the temperature layers plus the change in temperature

     Args:
        heating_rate: tha change in temperature over the change in time 
            in (K/s)
        Temp_layers: the temperature at every given layer in K
        delta_time: the time step for each layer

    Returns: The new temperature layers, but taking into a account the change 
        in tempreature

    """
    Temp_layers[:] =  Temp_layers[:] + heating_rate*delta_time
    return Temp_layers

def find_nearest(array,value):
    """
    finds the nearest value in array

    Args:
        array: the array for analyzing
        value: the value for which to finds
    Returns: 
        The value nearest to the one choses
    """
    idx = (np.abs(array-value)).argmin()
    return array[idx]

if __name__=="__main__":
    
    tot_trans=0.2
    num_layers=100
    p_sfc=1000.*1.e2
    p_top=100.*1.e2
    g=9.8
    T_sfc=300.
    Rd=287. #J/kg/K
    num_levels=num_layers+1
    tau_levels=find_tau(tot_trans,num_layers)
    press_levels=np.linspace(p_top,p_sfc,num_levels)
    press_diff=np.diff(press_levels)[0]
    press_levels=press_levels[::-1]
    press_layers=(press_levels[1:] + press_levels[:-1])/2.
    Temp_levels=np.ones([num_levels])*T_sfc
    Temp_layers=(Temp_levels[1:] + Temp_levels[:-1])/2.

    S0=241.
    Tc=273.15
    delta_time_hr=30   #time interval in hours
    delta_time_sec=30*3600.  #time interval in seconds
    stop_time_hr=600*24.  #stop time in hours
    times=np.arange(0,stop_time_hr,delta_time_hr) #times in hours
    tot_loops=len(times)
    num_times=len(times)
    #
    # Levels:
    #   num_levels, tau_levels, press_levels, Temp_levels
    # Layers:
    #   Temp_layers
    #
    sfc_temp=np.empty([num_times],dtype=np.float64)
    hours=np.empty_like(sfc_temp)
    #
    # sfc_temp is an array of random numbers used as placeholders
    # hours is an anray of zeros the same size as sfc_temp
    #
    air_temps=np.empty([num_layers,num_times],dtype=np.float64)
    up_flux_run=np.empty([num_levels,num_times],dtype=np.float64)
    down_flux_run=np.empty_like(up_flux_run)
    height_levels_run=np.empty_like(up_flux_run)

    dayss  = np.empty([num_layers,num_times],dtype=np.float64)
    
    for index in np.arange(0,num_times):
        rho_layers=press_layers/(Rd*Temp_layers)
        height_levels=find_heights(press_levels,rho_layers)
        up,down=fluxes(tau_levels,Temp_layers,T_sfc)
        sfc_temp[index]=T_sfc
        #
        # This loop gives the surface temperature for the length of sfc_temp
        #
        if np.mod(index,50)==0:
            the_frac=np.int(index/tot_loops*100.)
            sys.stdout.write("\rpercent complete: %d%%" % the_frac)
            sys.stdout.flush()
        air_temps[:,index]=Temp_layers[:]
        dayss[:,index] = press_layers[:]
        up,down=fluxes(tau_levels,Temp_layers,T_sfc)
        up_flux_run[:,index]=up[:]
        down_flux_run[:,index]=down[:]
        height_levels_run[:,index]=height_levels[:]
        dT_dt=heating_rate(up-down,height_levels,rho_layers)
        Temp_layers[:]=time_step(dT_dt,Temp_layers,delta_time_sec)
        #
        # display the percentage completed in multiples of 50 by the fraction.
        # air temps is a matrix of temperature of the layers, down flux, up flux are matricies
        # of downward and upward fluxes

        net_downsfc=S0 + down[0]
        
        
    plt.close('all')
    fig1,axis1=plt.subplots(1,1)
    snapshots=[0,2,8,30,40,50,60,70]
    days=times/24.
    for the_snap in snapshots:
        #
        # prints to the graph only the days included in snapshots
        #
        label="%3.1f" % days[the_snap]
        height_levels=height_levels_run[:,the_snap]
        layer_heights=(height_levels[1:] + height_levels[:-1])/2.
        axis1.plot(air_temps[:,the_snap],layer_heights*1.e-3,label=label)
        axis1.legend()
    axis1.set_title('temperature profiles for {} days'.format(len(snapshots)))
    axis1.set_xlabel('temperature (deg C)')
    fig1.savefig("snapshots.png")
   

    fig2,axis2=plt.subplots(1,1)
    axis2.plot(days,sfc_temp-Tc)
    axis2.set_title('surface temperature (deg C)')
    axis2.set_ylabel('temperature (degC)')
    axis2.set_xlabel('day')
    axis2.set_xlim((0,100))
    fig2.savefig("sfc_temp.png")

    fig3,axis3=plt.subplots(1,1)
    axis3.plot(days,sfc_temp - air_temps[0,:])
    axis3.set_title('air-sea temperature difference (deg C)')
    axis3.set_ylabel('surface - first layer temp (degC)')
    axis3.set_xlabel('day')
    axis3.set_xlim((0,100))
    fig3.savefig("air_sea.png")
    
    p1= find_nearest(press_levels,80000)
    p2= find_nearest(press_levels,50000)
    pos1 = np.where(press_levels==p1)
    pos2 = np.where(press_levels==p2)

    plt.close('all')
    fig4,axis4=plt.subplots(1,1)
    snapshots = [22,56]
    pres = press_levels/1000
    for the_snap in snapshots:

        label = "%3.1f" % pres[the_snap]
        height_levels = height_levels_run[:,the_snap]
        layer_heights=(height_levels[1:] + height_levels[:-1])/2.
        axis4.plot(dayss[:,the_snap]/24,layer_heights*1.e-3,label=label)
        axis4.legend()
    axis4.set_title(' {} pressures'.format(len(snapshots)))
    axis4.set_xlabel('Days')
    fig4.savefig("snaps.png")

    plt.show()

    
