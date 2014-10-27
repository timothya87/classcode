"""
   version 1  2014/10/25
"""

import numpy as np

h=6.63e-34  #planck's constant (J s)
kb=1.38e-23 # Boltzman's constant (J K^{-1})
c=3.e8  #speed of light (m/s)
c2=h*c/kb

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

def planckInt(wavel,Temp):
    print "inside planckInt"
    dlamb=wavel[1:] - wavel[:-1]
    bbr=planckwavelen(wavel[:-1],Temp)
    integ=np.sum(bbr*dlamb)
    return integ



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
    return out

#this trick will run  the following script if
#the file planck.py is run as a program, but won't
#if  planck.py is imported from another  module


if __name__ ==  '__main__':

    test_planck_wavelen()

##     Temp=262.
##     #check to see how good this approx. is:

##     wavel=11.e-6

##     bbr= planckwavelen(wavel,Temp)
##     bt = planckInvert(wavel,bbr)

##     print "pa: Temp (K), bbr (W/m^2/sr/m), bt (K): ",Temp,bbr*1.e-6,bt

##     wavel=np.arange(1.,2000.,.01)*1.e-6
##     print "size of  wavel: ",wavel.shape

##     bbr=planckwavelen(wavel,Temp)
##     print "size of  bbr: ",bbr.shape
##     print "type of bbr:", type(bbr)

##     totrad=planckInt(wavel,Temp)
##     stefan=5.67e-8*Temp**4.
##     print "approx integ: ",totrad," stefan-boltzman: ",stefan/np.pi

##     wavel=wavel*1.e6
##     totrad=planckInt(wavel,Temp)
##     stefan=5.67e-8*Temp**4.
##     print "approx Micron integ: ",totrad," stefan-boltzman: ",stefan/np.pi

    
## #check the derivitive

##     Temp=np.arange(284.,286.,0.1)
##     wavel=10.e-6
##     bbr= planckwavelen(wavel,Temp)
##     dbbrdT=(bbr[1:]-bbr[0:-1])/(Temp[1:]-Temp[0:-1])

##     Temp=285.
##     theDeriv=planckDeriv(wavel,Temp)
##     print "one deriv: ",dbbrdT[len(dbbrdT)/2]
##     print "two deriv: ",theDeriv


##     wavel=10.e-6
##     T0=320.
##     bbr=planckwavelen(wavel,300.)
##     guess=goodInvert(T0,bbr,wavel)
##     print "approx root with T0=299: ",guess

##     wavel=10.e-6
##     T0=320.
##     bbr=np.array([planckwavelen(wavel,300.),planckwavelen(wavel,310.),
##                   planckwavelen(wavel,290.)])
##     guess=rootfind(T0,bbr,wavel)
##     print "rootfind root with T0=320: ",guess

##     wavenum=np.arange(25,1600,20) #in inverse cm
##     c=3.e8
##     c_cm=c*100. #convert speed of light to cm/s
##     freq=c_cm*wavenum
##     Temp=280.
##     h=6.63e-34
##     kb=1.38e-23
##     print planckfreq(freq,Temp)
