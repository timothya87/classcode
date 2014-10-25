"""
   version 1  2014/10/25
"""

import numpy as np
from  scipy.integrate import quad

h=6.63e-34  #planck's constant (J s)
kb=1.38e-23 # Boltzman's constant (J K^{-1})
c=3.e8  #speed of light (m/s)
c2=h*c/kb
sigma=2.*np.pi**5.*kb**4./(15*h**3.*c**2.)

def WHplanck(wavel,Temp):
    """
       input: wavelength in meters, Temp in K
       output: blackbody radiance in W/m^2/m/sr
    """
    c1=3.74e-16  #W m^2
    c2=1.44e-2  #m K
    Blambda=c1/np.pi/(wavel**5.*(np.exp(c2/(wavel*Temp)) -1)) 
    return Blambda

def WHplanck(wavel,Temp):
    """
       input: wavelength in meters, Temp in K
       output: blackbody radiance in W/m^2/m/sr
    """
    c1=3.74e-16  #W m^2
    c2=1.44e-2  #m K
    Blambda=c1/np.pi/(wavel**5.*(np.exp(c2/(wavel*Temp)) -1)) 
    return Blambda

def planckDeriv(wavel,Temp):
    """
       input: wavel in m, Temp in K
       output: dBlambda/dlambda  W/m^2/m/sr/m
    """
    c1=3.74e-16 # W m^2
    c2=1.44e-2  #m K
    expterm=np.exp(c2/(wavel*Temp))
    deriv=c1/np.pi*wavel**(-6.)*(expterm -1)**(-2.)*c2/Temp**2.*expterm
    return deriv           


def planckwavelen(wavel,Temp):
    """
       input: wavelength (m), Temp (K)
       output: planck function W/m^2/m/sr
    """
    c1=2.*h*c**2.
    c2=h*c/kb
    Blambda=c1/(wavel**5.*(np.exp(c2/(wavel*Temp)) -1))
    return Blambda

def planckfreq(freq,Temp):
    """
      input: freq (Hz), Temp (K)
      output: planck function in W/m^2/Hz/sr
    """
    Bfreq=c1*freq**3./(np.exp(c2*freq/Temp) -1)
    c2=h/(kb*Temp)
    return Bfreq

def planckwavenum(waven,Temp):
    """
      input: wavenumber (m^{-1}), Temp (K)
      output: planck function in W/m^2/m^{-1}/sr
    """
    Bwaven=c1*waven**3./(np.exp(c2*waven/Temp) -1)
    c=3.e8
    c1=2.*h*c**2.
    kb=1.38e-23
    c2=h*c/(kb*Temp)
    return Bwaven


def planckInvert(wavel,Blambda):
    #note this is approximate!
    c1=3.74e-16
    c2=1.44e-2
    Tbright=c2/(wavel*(np.log(c1) -np.log(np.pi*wavel**5.) - np.log(Blambda)))
    return Tbright

def planckInt(Temp,lower,upper):
    """Integrate planckwavelen given temperatue Temp (K) from lower (m) to upper (m) wavelengths

       output: integrated radiance in W/m^2/sr
       see http://docs.scipy.org/doc/scipy-0.14.0/reference/integrate.html#module-scipy.integrate
    """
    args=(Temp)
    integ=quad(planckwavelen,lower,upper,args)
    return integ[0]


def goodInvert(T0,bbr,wavel):
    B0=planckwavelen(wavel,T0)
    theDeriv=planckDeriv(wavel,T0)
    delB=bbr-B0
    delT=delB/theDeriv
    theT=T0+delT
    return theT


def rootfind(T0,bbrVec,wavel):
    bbrVec=np.asarray(bbrVec)
    guess=planckwavelen(T0,wavel)
    out=[]
    for bbr in bbrVec:
        while np.fabs(bbr - guess) > 1.e-8:
            delB=bbr-guess
            deriv=planckDeriv(wavel,T0)    
            delT=delB/deriv
            T0=T0 + delT
            guess=planckwavelen(wavel,T0)
        out.append(T0)
    return out


def test_planck_wavelen():
    """
       test planck function for several wavelengths
       and Temps
    """
    #
    # need Temp in K and wavelen in m
    #
    the_temps=[200., 250., 350.]
    the_wavelens=np.array([8.,10.,12.])*1.e-6
    out=[]
    for a_temp in the_temps:
        for a_wavelen in the_wavelens:
            #
            # convert to W/m^2/micron/sr
            #
            the_bbr=planckwavelen(a_wavelen,a_temp)*1.e-6
            out.append(the_bbr)
    answer=[0.4498, 0.8921, 1.1922, 2.7226, 3.7736, 3.9804, 21.4025, 19.8225, 16.0759]
    np.testing.assert_array_almost_equal(out,answer,decimal=4)
    return None

def test_planck_inverse():
    """
       test planck inverse for several round trips
       and Temps
    """
    #
    # need Temp in K and wavelen in m
    #
    the_temps=[200., 250., 350.]
    the_wavelens=np.array([8.,10.,12.])*1.e-6
    out=[]
    for a_temp in the_temps:
        for a_wavelen in the_wavelens:
            #
            # convert to W/m^2/micron/sr
            #
            the_bbr=planckwavelen(a_wavelen,a_temp)
            out.append((a_wavelen,the_bbr))

    brights=[]
    for wavelen,bbr in out:
        brights.append(planckInvert(wavelen,bbr))
    answer=[200.0, 200.0, 200.0, 250.0, 250.0, 250.0, 350.0, 350.0, 350.0]
    np.testing.assert_array_almost_equal(brights,answer,decimal=10)
    return None

def test_planck_integral():
    """
       integrage and compare with stefan-boltzman
    """
    Temp=300.
    stefan=sigma/np.pi*Temp**4.
    totrad=planckInt(Temp,1.e-7,8000.e-6)
    np.testing.assert_almost_equal(totrad,stefan,decimal=5)
    return None

#this trick will run  the following script if
#the file planck.py is run as a program, but won't
#if  planck.py is imported from another  module


if __name__ ==  '__main__':

    test_planck_wavelen()
    test_planck_inverse()
    test_planck_integral()
