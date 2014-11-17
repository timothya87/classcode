import os,site
#
# import test functions from lib/planck.py
#
site.addsitedir(os.path.abspath('../lib'))
from planck import test_planck_wavelen,test_planck_inverse,test_planck_integral

test_planck_wavelen()
test_planck_inverse()
test_planck_integral()
