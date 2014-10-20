import numpy as np
import matplotlib.pyplot as plt
from radiances import find_tau,hydrostat

sigma=5.67e-8


def fluxes(tau,Temp,height,T_surf):
    up_rad=np.empty_like(height)
    down_rad=np.empty_like(height)
    sfc_rad=sigma*T_surf**4.
    up_rad[0]=sfc_rad
    tot_levs=len(tau)
    for index in np.arange(1,tot_levs):
        upper_lev=index
        lower_lev=index - 1
        del_tau=tau[upper_lev] - tau[lower_lev]
        trans=np.exp(-1.666*del_tau)
        emiss=1 - trans
        layer_rad=sigma*Temp[lower_lev]**4.*emiss
        #
        # find the radiance at the next level
        #
        up_rad[upper_lev]=trans*up_rad[lower_lev] + layer_rad
    #
    # start at the top of the atmosphere
    # with zero downwelling flux
    #
    down_rad[tot_levs-1]=0
    #
    # go down a level at a time, adding up the radiances
    #
    for index in np.arange(1,tot_levs):
        upper_lev=tot_levs - index
        lower_lev=tot_levs - index -1
        del_tau=tau[upper_lev] - tau[lower_lev]
        trans=np.exp(-1.666*del_tau)
        emiss=1 - trans
        layer_rad=sigma*Temp[upper_lev]**4.*emiss
        down_rad[lower_lev]=down_rad[upper_lev]*trans + layer_rad
    return (up_rad,down_rad)

def heating_rate(net_up,height,rho):
    cpd=1004.
    #
    # find the radiance divergence across the layer
    # by differencing the levels
    #
    rho_mid=(rho[1:] + rho[:-1])/2.
    dFn_dz= -1.*np.diff(net_up)/np.diff(height)
    dT_dt=dFn_dz/(rho_mid*cpd)
    return dT_dt

if __name__=="__main__":
    
    r_gas=0.01  #kg/kg
    k_lambda=0.01  #m^2/kg
    T_surf=300 #K
    p_surf=100.e3 #Pa
    dT_dz = -7.e-3 #K/km
    delta_z=10
    num_levels=1500
    Temp,press,rho,height=hydrostat(T_surf,p_surf,dT_dz,delta_z,num_levels)
    tau=find_tau(r_gas,k_lambda,rho,height)
    up,down=fluxes(tau,Temp,height,T_surf)
    dT_dt=heating_rate(up - down,height,rho)
    
    plt.close('all')
    fig1,axis1=plt.subplots(1,1)
    axis1.plot(up,height*0.001,'b-',lw=5,label='upward flux')
    axis1.plot(down,height*0.001,'g-',lw=5,label='downward lux')
    axis1.set_title('upward and downward fluxes')
    axis1.set_xlabel('flux $(W\,m^{-2})$')
    axis1.set_ylabel('height (km)')
    axis1.legend(numpoints=1,loc='best')

    fig2,axis2=plt.subplots(1,1)
    axis2.plot(up-down,height*0.001,'b-',lw=5)
    axis2.set_title('net upward flux')
    axis2.set_xlabel('net upward flux $(W\,m^{-2})$')
    axis2.set_ylabel('height (km)')

    dT_dt=heating_rate(up - down,height,rho)
    fig3,axis3=plt.subplots(1,1)
    #
    #find the height at mid-layer
    #
    layer_height=(height[1:] + height[:-1])/2.
    axis3.plot(dT_dt*3600.*24.,layer_height*0.001,'b-',lw=5)
    axis3.set_title('heating rate in K/day')
    axis3.set_xlabel('heating rate (K/day)')
    axis3.set_ylabel('height (km)')


    plt.show()

    
