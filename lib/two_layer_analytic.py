import numpy as np
sigma=5.67e-8

def troposphere(eps=0.5,S0=340):
    """
       input:  eps  (default=0.5) longwave emissivity of each layer
               S0   (default=340 W/m^2)  Solar constant
       output: Tground, T1, T2  (all Kelvins)  -- equilibrium temperatures of ground, first and second layer
               see the google spreadsheet at:  
               https://docs.google.com/spreadsheets/d/1bnWUHHrof-0tzZlCDGAL1L74KAqls0XRttpK3AMrhCQ/edit#gid=1066209610
               for the equations that were solved
               https://docs.google.com/spreadsheets/d/1NfI1gRkhuFvSupDX3RF4D2YBGPfuAWH-mpYDDJHu4HE/edit#gid=923351782
    """
    b6=eps
    b7=S0
    sigma=5.67e-8
    Fground=(1-0.3)*b7/(1-b6/2*(1+b6*(1-b6)/2)/(1-b6*b6/4)-(1-b6)*b6/2*((1-b6)+b6/2)/(1-b6*b6/4))
    c4=Fground
    F1=c4*b6/2*(1+b6*(1-b6)/2)/(1-b6*b6/4)
    F2=c4*b6/2*((1-b6)+b6/2)/(1-b6*b6/4)
    Tground=(Fground/(sigma))**0.25
    #
    # convert to temperature assuming greybody
    #
    T1=(F1/(sigma*eps))**0.25
    T2=(F2/(sigma*eps))**0.25
    return Tground,T1,T2

def stratosphere(eps_l=0.03,eps_s=0.10,S0=340):
    """
       input:  eps_l  (default=0.03) longwave emissivity due to CO2 of each layer
               eps_s (default=0.10)  shortwave absorptivity due to O3 of each layer
               S0   (default=340 W/m^2)  Solar constant
       output: T1, T2  (all Kelvins)  -- equilibrium temperatures of first and second layer
               see the google spreadsheet at:  
               https://docs.google.com/spreadsheets/d/1bnWUHHrof-0tzZlCDGAL1L74KAqls0XRttpK3AMrhCQ/edit#gid=1066209610
               for the equations that were solved
    """
    B6=S0
    B5=eps_l
    B4=eps_s
    F2=B6*(B4/2+B4*(1-B4)*B5/4)/(1-B5*B5/4)
    F1=B6*(B4*(1-B4)/2+B5*B4/4)/(1-B5*B5/4)
    #
    # convert to temperature assuming greybody
    #
    T1=(F1/(sigma*eps_l))**0.25
    T2=(F2/(sigma*eps_l))**0.25
    return T1,T2       

if __name__=="__main__":
    import matplotlib.pyplot as plt
    #
    # run default cases to check
    #
    Tground,T1,T2=troposphere()
    ST1,ST2=stratosphere()
    print("default tropospheric ground, layer 1 and layer 2 temps: {:5.2f} K, {:5.2f} K, {:5.2f} K".format(Tground,T1,T2))
    print("default stratospheric layer 1 and layer 2 temps: {:5.2f} K, {:5.2f} K".format(T1,T2))
    print(ST1,ST2)
    Tg_vals=[]
    T1_vals=[]
    T2_vals=[]
    eps=np.linspace(0.3,0.6,100)
    for the_eps in eps:
        Tground,T1,T2=troposphere(eps)
        Tg_vals.append(Tground)
        T1_vals.append(T1)
        T2_vals.append(T2)
    fig=plt.figure(1)
    fig.clf()
    ax1=fig.add_subplot(111)
    ax1.plot(eps,T1,label='layer 1 temp (K)')
    ax1.plot(eps,T2,label='layer 2 temp (K)')
    ax1.legend(loc='upper left')
    ax1.set_xlabel('emmissivty $\epsilon$')
    ax1.set_ylabel('layer temperature (K)')
    ax1.set_title('tropospheric temperatures with S0/4=340 $W/m^2$')
    fig.tight_layout()
    fig.canvas.draw()

    eps=np.linspace(0.01,0.05,100)
    for the_eps in eps:
        T1,T2=stratosphere(eps)
        T1_vals.append(T1)
        T2_vals.append(T2)
    fig=plt.figure(2)
    fig.clf()
    ax1=fig.add_subplot(111)
    ax1.plot(eps,T1,label='layer 1 temp (K)')
    ax1.plot(eps,T2,label='layer 2 temp (K)')
    ax1.legend(loc='upper right')
    ax1.set_xlabel('emmissivty $\epsilon$')
    ax1.set_ylabel('layer temperature (K)')
    ax1.set_title('stratospheric temperatures with S0/4=340 $W/m^2$')
    fig.tight_layout()
    fig.canvas.draw()
    plt.show()
    
