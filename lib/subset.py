#!/usr/bin/env python
from __future__ import print_function
import types
import h5py
from modismeta_h5 import parseMeta
from h5dump import dumph5
import glob,os
import argparse

def output_h5(level1b_file,geom_file,output_name):
    """
        input:  two input filenames or h5py.File objects
          level1b_file
          geom_file
        that contain the
        level1b radiances and reflectivities from Laadsweb and the
        full pixel latitude and longitudes
        and one filename:
           outpout_name
        that is the name of the file to write the subsetted data to.
        output:  side effect -- writes an output file with new datasets
          chan1, chan31, latitude, longitude and metadata
    """
    def openfile(filename):
        if isinstance(filename,types.StringType):
            infile = h5py.File(filename,'r')
        elif isinstance(filename,h5py._hl.files.File):
            infile=filename
        else:
            raise IOError, "need an h5 filename or h5.File instance"
        return infile
    l1b_file=openfile(level1b_file)
    geom_file=openfile(geom_file)
    #channel31 is emissive channel 10
    index31=10
    chan31=l1b_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_1KM_Emissive'][index31,:,:]
    scale=l1b_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_1KM_Emissive'].attrs['radiance_scales'][index31]
    offset=l1b_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_1KM_Emissive'].attrs['radiance_offsets'][index31]
    chan31=(chan31 - offset)*scale
    index1=0  #channel 1 is first 250 meter reflective channel
    reflective=l1b_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_250_Aggr1km_RefSB'][0,:,:]
    scale=l1b_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_250_Aggr1km_RefSB'].attrs['reflectance_scales']
    offset=l1b_file['MODIS_SWATH_Type_L1B']['Data Fields']['EV_250_Aggr1km_RefSB'].attrs['reflectance_offsets']
    chan1=(reflective - offset[0])*scale[0]
    the_lon=geom_file['MODIS_Swath_Type_GEO']['Geolocation Fields']['Longitude'][...]
    the_lat=geom_file['MODIS_Swath_Type_GEO']['Geolocation Fields']['Latitude'][...]

    with h5py.File(output_name, "w") as f:
        dset = f.create_dataset("lattitude", the_lat.shape, dtype=the_lat.dtype)
        dset[...]=the_lat[...]
        dset = f.create_dataset("longitude", the_lon.shape, dtype=the_lon.dtype)
        dset[...]=the_lon[...]
        dset = f.create_dataset("channel1", chan1.shape, dtype=chan1.dtype)
        dset[...]=chan1[...]
        dset = f.create_dataset("channel31", chan31.shape, dtype=chan31.dtype)
        dset[...]=chan31[...]
        metadata=parseMeta(l1b_file)    
        for the_key in metadata.keys():
            f.attrs[the_key]=metadata[the_key]
    return None
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('l1b21km',  type=str,help='path to Modis Level 1b h5 file (MYD021KM or MOD021KM)')
    parser.add_argument('geom03',  type=str,help='path to  Modis Level geometry file (MYD03 or MOD03)')
    parser.add_argument('output', nargs='?', type=str,default='subset.h5',help='path to of h5 output file (will overwrite if exists)')
    args=parser.parse_args()
    if os.path.exists(args.output):
        print("deleting output file {}".format(args.output))
        os.remove(args.output)
    l1b_file=glob.glob(args.l1b21km)[0]
    geom_file=glob.glob(args.geom03)[0]
    output_h5(l1b_file,geom_file,args.output)
