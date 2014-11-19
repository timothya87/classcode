from matplotlib import pyplot as plt
import numpy as np

def function_H(Temp,height):
    R_d=287.
    g=9.8
    num_temps=len(Temp)
    inv_scale_height=0
    for index in range(num_temps - 1):
        delta_z=height[index+1] - height[index]
        inv_scale_height=inv_scale_height + \
               g/(R_d*Temp[index])*delta_z
    avg_inv_scale_height=inv_scale_height/height[-1]
    avg_scale_height=1/avg_inv_scale_height
    return avg_scale_height

def function_H_vec(Temp,height):
    R_d=287.
    g=9.8
    num_temps=len(Temp)
    function=g/(R_d*Temp[:-1])
    delta_z=np.diff(height)
    the_int=np.sum(function*delta_z)
    the_avg=the_int/height[-1]
    scale_height=1./the_avg
    return scale_height

def press_int(heights,Temp,p0):
    Rd=287.
    g=9.8
    dz=np.diff(heights)
    function= -g/(Rd*Temp[:-1])
    log_p_p0=np.cumsum(function*dz)
    p_p0=np.exp(log_p_p0)
    p_p0=np.concatenate(([1.],p_p0))
    press_vec=p0*p_p0
    return press_vec

if __name__=="__main__":
    ztop=2.e4
    p0=1.e5
    T0=280.
    heights=np.linspace(0,ztop,100.)
    Temp=  T0 -7.e-3*heights
    #Temp=np.empty_like(heights)
    #Temp[:]=T0
    press_vec=press_int(heights,Temp,p0)
    scale_height=function_H(Temp,heights)
    scale_height_II=function_H_vec(Temp,heights)
    press_scale=p0*np.exp(-heights/scale_height)
    plt.close('all')
    fig=plt.figure(1)
    ax=fig.add_subplot(111)
    ax.plot(press_vec*1.e-3,heights*1.e-3)
    ax.plot(press_scale*1.e-3,heights*1.e-3,'r+')
    plt.show()
    
    
    
    
