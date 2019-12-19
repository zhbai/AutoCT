import numpy as np
import os
import sys
from glob import glob
import subprocess
from subprocess import call, check_output
import shlex

def sortKeyFunc(s):
    return (os.path.basename(s).split('/')[-1][:7])

if __name__ == '__main__':
    file_names = glob("/Users/zhebai/documents/TBI/results/STD/F_16_30_clinical/Measurements/Warp_jacobian/*Jacobian.nii.gz")
    file_names.sort(key = sortKeyFunc)
    print(file_names)
    template = "../HarvardOxford-sub-maxprob-thr25-1mm.nii.gz" #HarvardOxford-cort-maxprob-thr25-1mm.nii.gz
    #ourT_MNI_all_label_CTInverseWarped.nii.gz"
    #ourT_MNI_Harvardoxford_sub_label_CTInverseWarped.nii.gz
    for i in range(len(file_names)):
        file_name = file_names[i]
        output_name = file_name.split('/')[-1][:7]+""

#        sys.stdout = open(output_name+".txt", 'w')
        print("Procss file name: ", output_name)
#        command_line = antsRegistrationSyNQuick.sh -d 3 -f template -m file -t s -o file+"_registered"
#        call(shlex.split(command_line))

#        p = subprocess.Popen(['imageintensityStatistics', '3', file_name, template], stdout=subprocess.PIPE)
#        print(p.communicate())
#        check_output(['imageintensityStatistics', '3', file_name, template])
#        print(output, sep=' ', end = '\n', flush = True)
        call(['ImageIntensityStatistics', '3', file_name, template])

