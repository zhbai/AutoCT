############################## 
# Author: Talita Perciano    #
# Aug 2019                   #
##############################

import numpy as np
from skimage import io
import matplotlib.pyplot as plt
from scipy import misc
import os

from glob import glob
import dicom2nifti
import dicom2nifti.settings as settings

settings.disable_validate_orthogonal()
settings.disable_validate_sliceincrement()
settings.disable_validate_orientation()
settings.enable_resampling()
settings.set_resample_spline_interpolation_order(1)
settings.set_resample_padding(-1000)

if __name__ == '__main__':
    folder_names = glob("/home/users/tperciano/Dropbox/LBL_Projects/TBI_project/ClinicalCTs/Young_F/TBI_YOUNG_F/PI-1076/Ct Head Or Brain Witho 3356917272105973 20100904/*/")
    for i in range(len(folder_names)):
        folder = folder_names[i]
        output_name = folder.split('/')[-2]+".nii"
        print("Output name: ", output_name)
        try:
            dicom2nifti.dicom_series_to_nifti(folder, output_name, reorient_nifti=True)
        except:
            pass

