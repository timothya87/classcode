import numpy as np

def rad_eqn(Pr,R,La,K2):
	"""
	Finds The reflectivity factor Z

    Args:
        Pr: the recieved power in Dbm
        R: range in km
        La: the attention
        K2: The efficiency of scattering in microwaves

    Returns:
        The reflectivity factor z

	"""

	Pt = 750000. #w
	R1 = 2.17e-10 # km
	z1 = 1. # mm^6/m^3
	b  = 14255.
	Pr = (10.**(Pr/10.))/1000. # W


	Z = (Pr/Pt)*(La/K2)*(R/R1)**2*(1./b)*z1
	return Z


def RR_eqn(Z):

	"""
	Finds the rainfall rate in mm/hr

	Args:
		Z: the reflectivity factor from rad_eqn

	Returns:
		the rainfall rate in mm/hr
	"""
	RR = np.exp(np.log(Z/2000.)/2.)

	return RR

if __name__=="__main__":

	Z = rad_eqn(-58,100,1,0.93)
	RR = RR_eqn(Z)

	print "Rainfall rate       = %4.2f  mm/hr" % RR
	print "Reflectivity factor = %8.2f mm^6/m^3" % Z
	print""

	Z1 = rad_eqn(-58,100,1,0.208)
	RR1 = RR_eqn(Z1)

	Z2 = rad_eqn(-58,100,2,0.93)
	RR2 = RR_eqn(Z2)

	print "1. Rainfall rate    = %4.2f mm/hr" % RR1
	print "   Reflec factor    = %4.2f mm^6/m^3" % Z1
	print "2. Rainfall rate    = %4.2f mm/hr" % RR2
	print "   Reflec factor    = %4.2f mm^6/m^3" % Z2
