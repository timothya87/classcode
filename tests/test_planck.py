import os,site
site.addsitedir(os.path.abspath('../lib'))
from planck import test_planck_wavelen

test_planck_wavelen()

