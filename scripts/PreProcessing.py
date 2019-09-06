############################## 
# Author: Talita Perciano    #
# Aug 2019                   #
##############################


import os, shutil
import numpy as np

OriginalPath = "/home/users/tperciano/Dropbox/LBL_Projects/TBI_project/ClinicalCTs/Young_M/Original/"
OutputPath = "/home/users/tperciano/Dropbox/LBL_Projects/TBI_project/ClinicalCTs/Young_M/Preprocessed/"
MNIPath = "/home/users/tperciano/Dropbox/LBL_Projects/TBI_project/ClinicalCTs/MNI/"
files = os.listdir(OriginalPath)
files.sort()

for f in files:
    os.system('fslswapdim ' + OriginalPath+f + ' x -y z out1.nii.gz')
    os.system('3dresample -dxyz 1.0 1.0 1.0 -orient RPI -prefix out2.nii.gz -inset out1.nii.gz')
    os.system('robustfov -i out2.nii.gz -r out3.nii.gz')
    os.system('$ANTSPATH/N4BiasFieldCorrection -d 3 -i out3.nii.gz -o out3.nii.gz')
    os.system('~/Dropbox/LBL_Projects/TBI_project/Registration/ANTs/Scripts/antsRegistrationSyN.sh -d 3 -n 40 -f ' + MNIPath+'MNI152_T1_1mm.nii.gz -m out3.nii.gz -o ' + OutputPath+f.split('.')[0] + '_normalized -t a')
    os.remove('out1.nii.gz')
    os.remove('out2.nii.gz')
    os.remove('out3.nii.gz')

os.system('Rscript skull_strip.R')
