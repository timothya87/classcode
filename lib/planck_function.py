import numpy as np 
c=2.99792458e+08  #m/s -- speed of light in vacumn
h=6.62606876e-34  #J s  -- Planck's constant
kb=1.3806503e-23  # J/K  -- Boltzman's constant

def planckwavelen(wavel,Temp):
    """input wavelength in microns and Temp in K, output
    bbr in W/m^2/micron/sr
    """
    wavel=wavel*1.e-6  #convert to meters
    c1=2.*h*c**2.
    c2=h*c/kb
    Blambda=1.e-6*c1/(wavel**5.*(np.exp(c2/(wavel*Temp)) -1))
    return Blambda
