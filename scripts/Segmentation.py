import numpy as np
from skimage import io
import matplotlib.pyplot as plt
from scipy import misc
import os
import time
from glob import glob

#path = os.getcwd()
path = os.path.abspath(__file__ + "/../../results/STD/M_16_30/")
Template = path + "/TemplateYoungM_128.nii.gz"
Atlas = path + "/../F_16_30_clinical/HarvardOxford-cort-maxprob-thr25-1mm.nii.gz" #/../F_16_30_clinical/

OutputPath = path + "/SEG/"

if __name__ == '__main__':
    folder_names = glob("/Users/zhebai/Documents/TBI/results/STD/M_16_30/Preprocessed/PI-1152*skull.nii.gz")
    #glob("/Users/zhebai/Documents/TBI/results/STD/F_16_30_clinical/severe/*/*/*AXIALS 2 */")
    #print(folder_names)
    for i in range(len(folder_names)):
        folder = folder_names[i]
        output_name = folder.split('/')[-1] #+".nii.gz"
        output_path_name = os.path.join(path, output_name)
        print(os.path.join(path, output_name))
        #output_name = check_and_rename(os.path.join(path, output_name))
        print("Output name: ", output_name)
        #print("folder name: ", folder)

        Input_Physic = os.path.join(path + "/Preprocessed/", output_name[:7])
        
        Output_SyN = os.path.join(path + "/REGIS/SyN/", output_name[:7])
        Output_Affine = os.path.join(path + "/REGIS/Affine/", output_name[:7])
        Output_Affine2SyN = os.path.join(path + "/REGIS/Affine2SyN/", output_name[:7])
        
        #3 stages: rigid + affine + deformable syn (default = 's')
        print("REGISTRATING:", i)
        os.system('antsRegistrationSyNQuick.sh -d 3 -n 4 -f ' + Template + ' -m ' + Input_Physic + '_preprocessed_skull.nii.gz -o ' + Output_SyN + '_preprocessed_SyN')
        #2 stages: rigid + affine
        os.system('antsRegistrationSyNQuick.sh -d 3 -n 4 -f ' + Template + ' -m ' + Input_Physic + '_preprocessed_skull.nii.gz -o ' + Output_Affine + '_preprocessed_affine -t a')
        #1 stage: deformable syn only
        os.system('antsRegistrationSyNQuick.sh -d 3 -n 4 -f ' + Template + ' -m ' + Output_Affine + '_preprocessed_affineWarped.nii.gz -o ' + Output_Affine2SyN + '_preprocessed_affine2SyN -t so')

        #SEGMENTATION OF THE ORIGINAL CT SCAN OF PATIENT
        print("SEGMENTING:", i)
        start = time.time()
        OutputSeg = path + "/SEG/PHYSCi/" + output_name[:7]
        os.system('antsApplyTransforms -f 0 -d 3 -n GenericLabel[Linear] -i ' +  Atlas + ' -o ' + OutputSeg + '_segmentation_cortical_phy.nii.gz -r ' + Input_Physic + '_preprocessed_skull.nii.gz -t [' + Output_SyN + '_preprocessed_SyN0GenericAffine.mat,1] ' +  Output_SyN + '_preprocessed_SyN1InverseWarp.nii.gz')
        end = time.time()
        print("Physical: ", end - start)
#        #SEGMENTATION OF THE AFFINE TRANSFORMED DATA
        OutputSeg = path + "/SEG/AFFINE/" + output_name[:7]
        os.system('antsApplyTransforms -f 0 -d 3 -n GenericLabel[Linear] -i ' +  Atlas + ' -o ' + OutputSeg + '_segmentation_cortical_affine.nii.gz -r ' + Output_Affine + '_preprocessed_affineWarped.nii.gz -t [' + Output_Affine2SyN + '_preprocessed_affine2SyN0GenericAffine.mat,1] ' +  Output_Affine2SyN + '_preprocessed_affine2SyN1InverseWarp.nii.gz')
        end = time.time()
        print("Affine: ", end - start)
