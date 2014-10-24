"""
   this script generates a hydrostatic atmosphere then finds optical
   depths at 7 different wavelengths given assumed k values for CO2.  It differences
   the transmissivities to get the weighting functions following
   Stull eq. 8.4
"""

import numpy as np
import matplotlib.pyplot as plt
from hydrostat import hydrostat


def find_tau(r_gas,k_lambda,rho,height):
    """
       input: r_gas -- gas mixing ratio in kg/kg
              k_lambda -- mass absorption coefficient in kg/m^2
              rho -- vector of air densities in kg/m^3
              height -- corresponding layer heights in m
       output:  tau -- vetical optical depth from the surface, same shape as rho
    """
    tau=np.empty_like(rho)
    #
    # start at TOA with tau=0 and work down
    #
    tau[-1]=0
    num_levels=len(rho)
    num_layers=num_levels-1
    for index in range(num_layers):
        top_index=num_layers - index 
        bot_index=num_layers - index - 1
        delta_z=height[top_index] - height[bot_index]
        delta_tau=r_gas*rho[top_index]*k_lambda*delta_z
        tau[bot_index]=tau[top_index] + delta_tau
    return tau     

if __name__=="__main__":
    r_gas=0.01  #kg/kg
    T_surf=300 #K
    p_surf=100.e3 #Pa
    dT_dz = -7.e-3 #K/km
    delta_z=100
    num_levels=250
    #
    # assign the 7 k_lambdas to 7 CO2 absorption band wavelengths
    # (see Wallace and Hobbs figure 4.33)
    #
    wavenums=np.linspace(666,766,7)
    wavelengths=1/wavenums
    print wavelengths*1.e4  #microns
    #
    # make a hydrostatic atmosphere
    #
    Temp,press,rho,height=hydrostat(T_surf,p_surf,dT_dz,delta_z,num_levels)
    #
    #
    #  I played around with the k values -- multiplying by 5 gave me
    #  weighting functions that peaked at the right height
    #
    k_lambda=np.array([0.002,0.003,0.006,0.010,0.012,0.016,0.020])*5.  
    legend_string=["%5.3f" % item for item in k_lambda]
    #
    # make a list of tuples of k_lambda and its label
    # using zip
    #
    k_vals=zip(k_lambda,legend_string)
    #
    #  find the height at mid-layer
    #
    plt.close('all')
    mid_height=(height[1:] + height[:-1])/2.
    fig1,axis1=plt.subplots(1,1)
    fig2,axis2=plt.subplots(1,1)
    fig3,axis3=plt.subplots(1,1)
    for k_lambda,k_label in k_vals:
        tau=find_tau(r_gas,k_lambda,rho,height)
        axis1.plot(tau,height,label=k_label)
        trans=np.exp(-tau)
        axis2.plot(trans,height,label=k_label)
        del_trans=np.diff(trans)
        axis3.plot(del_trans,mid_height,label=k_label)
    axis1.set_title('optical depth for 7 values of $k_\lambda$')
    axis1.set_xlabel('optical depth')
    axis2.set_xlabel('transmittance')
    axis3.set_xlabel('weighting function')
    axis2.set_title('transmittance for 7 values of $k_\lambda$')
    axis3.set_title('weighting function for 7 values of $k_\lambda$')
    axis1.legend(loc='best')
    axis2.legend(loc='best')
    axis3.legend(loc='best')
    axis_list=[axis1,axis2,axis3]
    [the_axis.set_ylabel('height (km)') for the_axis in axis_list]
    fig1.savefig('transmit_opticaldepth.png')
    fig2.savefig('transmit_top.png')
    fig3.savefig('transmit_weights.png')
    plt.show()

    
