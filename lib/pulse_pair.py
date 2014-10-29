import matplotlib.pyplot as plt
from numpy import pi
import numpy as np

fig1=plt.figure(1)
fig1.clf()
axis1=fig1.add_subplot(111,polar=True)
theta=np.array([0.,0.])*pi/180.;
rho=np.array([0.,1.]);
line1=axis1.plot(theta,rho,'b-',linewidth=3);
point1=axis1.plot(0,1,'bo');

theta=np.array([30.,30.])*pi/180.;
rho=np.array([0,1]);
line1=axis1.plot(theta,rho,'c-',lw=4);
point1=axis1.plot(theta[0],1,'co');

theta=np.array([60.,60.])*pi/180.;
rho=np.array([0,1]);
line1=axis1.plot(theta,rho,'g-',lw=4);
point1=axis1.plot(theta[0],1,'go');

theta=np.array([90.,90.])*pi/180.;
rho=np.array([0,1]);
line1=axis1.plot(theta,rho,'k-',lw=4);
point1=axis1.plot(theta[0],1,'ko');
axis1.set_title('phase shifts of 0, 30, 60, 90 degrees')
fig1.canvas.draw()
plt.show()
