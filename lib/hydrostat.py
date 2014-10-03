#updated 2012/10/14 to change num_layers to num_levels
import numpy as np
import matplotlib.pyplot as plt

def hydrostat(T_surf,p_surf,dT_dz,delta_z,num_levels):
    """
       build a hydrostatic atmosphere by integrating the hydrostatic equation from the surface,
       using num_layers=num_levels-1 of constant thickness delta_z
       input:  T_surf -- surface temperature in K
              p_surf -- surface pressure in Pa
              dT_dz -- constant rate of temperature change with height in K/m
              delta_z  -- layer thickness in m
              num_levels -- number of levels in the atmosphere
       output:
              numpy arrays: Temp (K) , press (Pa), rho (kg/m^3), height (m)
    """
    Rd=287. #J/kg/K  -- gas constant for dry air
    g=9.8  #m/s^2
    Temp=np.empty([num_levels])
    press=np.empty_like(Temp)
    rho=np.empty_like(Temp)
    height=np.empty_like(Temp)
    num_layers=num_levels-1
    #
    # layer 0 sits directly above the surface, so start
    # with pressure, temp of air equal to ground temp, press
    # and get density from equaiton of state
    # 
    press[0]=p_surf
    Temp[0]=T_surf
    rho[0]=p_surf/(Rd*T_surf)
    height[0]=0
    #
    #now march up the atmosphere a layer at a time
    #using the hydrostatic equation from the Beer's law notes
    #
    for i in range(num_layers):
        delP= -rho[i]*g*delta_z
        height[i+1] = height[i] + delta_z
        Temp[i+1] = Temp[i] + dT_dz*delta_z
        press[i+1]= press[i] + delP
        rho[i+1]=press[i+1]/(Rd*Temp[i+1])
    return (Temp,press,rho,height)

def find_tau(r_gas,k_lambda,rho,height):
    """
       input: r_gas -- gas mixing ratio in kg/kg
              k_lambda -- mass absorption coefficient in kg/m^2
              rho -- vector of air densities in kg/m^3
              height -- corresponding level heights in m
       output:  tau -- vetical optical depth from the surface, same shape as rho
    """
    print r_gas,k_lambda
    tau=np.empty_like(rho)
    tau[0]=0
    num_levels=len(rho)
    num_layers=num_levels-1
    #
    # see Wallace and Hobbs equation 4.32
    #
    for index in range(num_layers):
        delta_z=height[index+1] - height[index]
        delta_tau=r_gas*rho[index]*k_lambda*delta_z
        tau[index+1]=tau[index] + delta_tau
    return tau     

if __name__=="__main__":
    r_gas=0.01  #kg/kg
    k_lambda=0.01  #m^2/kg
    T_surf=300 #K
    p_surf=100.e3 #Pa
    dT_dz = -7.e-3 #K/km
    delta_z=1
    num_levels=15000    
    Temp,press,rho,height=hydrostat(T_surf,p_surf,dT_dz,delta_z,num_levels)
    tau=find_tau(r_gas,k_lambda,rho,height)
    fig1,axis1=plt.subplots(1,1)
    axis1.plot(tau,height*1.e-3)
    axis1.set_title('vertical optical depth vs. height')
    axis1.set_ylabel('height (km)')
    axis1.set_xlabel('optical depth (no units)')
    fig2,axis2=plt.subplots(1,1)
    axis2.plot(tau,press*1.e-3)
    axis2.invert_yaxis()
    axis2.set_title('vertical optical depth vs. pressure')
    axis2.set_ylabel('pressure (kPa)')
    axis2.set_xlabel('optical depth (no units)')
    plt.show()    



            #
            
            
     
     
                   
