# -*- coding: utf-8  -*-
from __future__ import print_function
from __future__ import division  #comment out this line and watch what happens to A23
import numpy as np
from stull_radar_II import findRR_rain

#A21:  Cumulative Rainfall
#
# tuples contain (start time, stop time, dbZ)
#

time_dbZ=[(0,10,15),(10,25,30),(25,29,43),(29,30,50),(30,55,18),(55,60,10)]
total=0
minutes=0
for start,stop,dbZ in time_dbZ:
    RR=findRR_rain(dbZ)
    duration=(stop - start)
    total+= RR*duration
    minutes+=duration
text="""
   Problem A21:  Cumulative Rainfall totals

   total rainfall is {:5.1f} cm over {:d} minutes
   """.format(total/10.,minutes)
print(text)

#A22:  Doppler shifts

def stull_8_32(Mr,the_lambda):
    """
       input:  Mr (radial velocity) m/s, pos. away from radar
               the_lambda (radar wavelength, m)
       output: doppler frequency shift, in Hz (positive into the radar)
    """
    del_freq= -2.*Mr/the_lambda
    return del_freq
    
#
# velocities in m/s
#
A22_items=[('a.', -110), ('b.', -85), ('c.', -60), ('d.',-20),\
            ('e.', 90),('f.', 65),('g.',40),('h.',30)]
the_lambda=0.1  #radar wavelength in meters
A22_output=[(letter,veloc,stull_8_32(veloc,the_lambda)) for letter,veloc in A22_items]

carrier_freq=3.e8/0.1   #base frequency is 3 GHz

output_line="    {:s}: velocity {:3.0f} m/s \t doppler shift: {:5.1f} Hz, \t doppler shift as fraction of 3 GHz: {:8.3g}\n"

results='\n'
for letter,veloc,shift in A22_output:
    results += output_line.format(letter,veloc,shift,shift/carrier_freq)

text="""
   Problem A22:  Doppler Shifts

   {}
    """.format(results)

print(text)
      
#A23:  Velocity folding

def find_folded(velocity,Mrmax):
    #
    # first remove any full rotations (360 degrees)
    # from the velocity
    #
    #
    sign=np.sign(velocity)   #could use velocity/np.abs(velocity)
                             # but that blows up at 0 velocity
    full_rotations=int(velocity/(2.*Mrmax))
    if full_rotations > 0:
        residual=np.abs(velocity) - full_rotations*2.*Mrmax
        velocity=residual*sign
    fraction=velocity/Mrmax   #fraction of pi
    if np.abs(fraction) > 1.:   #more than 180 degrees
                        #so go the other direction and change sign
        ## if sign > 0:                  
        ##     fraction = -(2. - fraction)
        ## if sign < 0:
        ##     fraction = (2. + fraction)
        #
        # this one-liner is the same as above if statements
        #
        fraction = -sign*(2 - np.abs(fraction))
    return fraction*Mrmax

A23_pairs=[('a.',26.),('b.',28),('c.',30.),('d.',35.),('e.',20.),('f.',25),
        ('g.',55.),('h.',-26),('i.',-28),('j.',-30.),('k.',-35),('l.',-20)]        

Mrmax=25        
A23_output=[(letter,veloc,find_folded(veloc,Mrmax)) for letter,veloc in A23_pairs]    

#
# build up the output a line at a time, accumulating lines in the results string
#
output_line="    {:s}: velocity {:+4.0f} m/s \t the radar displays: {:+4.0f} m/s\n"

results='\n'
for letter,veloc,folded in A23_output:
    results += output_line.format(letter,veloc,folded)

text="""
   Problem A23:  Doppler velocity folding for Mrmax of {} m/s

   {}
    """.format(Mrmax,results)

print(text)

#A24  range folding

def find_range(range,Rmax):
    range_multiples=int(range/Rmax)
    residual=range - range_multiples*Rmax
    return residual

A24_pairs=[('a.',205.),('b.',210.),('c.',250.),('d.',300.),('e.',350.),('f.',400.),
            ('g.',230.),('h.',240),('i.',390.),('j.',410.)]

Rmax=200.

A24_output=[(letter,Range,find_range(Range,Rmax)) for letter,Range in A24_pairs]    

#
# build up the output a line at a time, accumulating lines in the results string
#
output_line="    {:s}: Range {:+4.0f} km \t the radar displays: {:+4.0f} km\n"

results='\n'
for letter,Range,folded in A24_output:
    results += output_line.format(letter,Range,folded)

    
text="""
   Problem A24:  Radar range folding for an Rmax of {} km

   {}
    """.format(Rmax,results)
    
print(text)
