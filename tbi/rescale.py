#!/usr/bin/env python

import nibabel as nib
import numpy as np

def rescale(img, aamin=-1024, aamax=3071):
   print("tbi:min = ", aamin)
   print("tbi:max = ", aamax)
   data = img.get_fdata()
   tmin, tmax = np.amin(data), np.amax(data)
   print("tbi:tmin = ", tmin)
   print("tbi:tmax = ", tmax)

   if tmin < aamin or tmax > aamax:
      data[data < aamin] = aamin 
      data[data > aamax] = aamax 

   ret = nib.Nifti1Image(data, img.affine, img.header)
   ret.header.set_data_dtype(np.float32) 
   ret.header['descrip'] = b'written by dcm2nii - '
   #ret.header['scl_slope'] = 1.0
   #ret.header['scl_inter'] = 0.0
   #ret.header.set_slope_inter(1.0, 0.0)
   ret.header['cal_max'] = tmax
   ret.header['cal_min'] = tmin 
   ret.header['glmax'] = tmax
   ret.header['glmin'] = tmin 
   return ret 
