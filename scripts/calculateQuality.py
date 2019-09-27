############################## 
# Author: Talita Perciano    #
# Aug 2019                   #
##############################


import matplotlib.pyplot as plt
import numpy as np 
import nibabel as nib
import sys                                                                                                                                                                                               
sys.path.append('/home/users/tperciano/Software/libsvm-3.23/python/') 
import brisque.brisque

brisq = brisque.BRISQUE()

########## AVERAGE START  ###############

num_cts = [2, 4, 8, 16, 32, 64, 128, 158]
input_path = '/home/users/tperciano/Dropbox/LBL_Projects/TBI_project/ClinicalCTs/Young_F/Templates/'


templates_average = []
scores_average_start_affine = []
templates_ref = []
scores_ref_start_affine = []

for i in num_cts:
    input_name = input_path + str(i) + '/AverageStart/' + str(i) + '_affine/out/T_template0.nii.gz'
    template = nib.load(input_name)
    templates_average.append(np.array(template.dataobj))

for template in templates_average:
    x, y, z = template.shape
    average = 0
    valid = 0
    for i in range(z):
        img_slice = template[:,:,i]
        #img_slice = (img_slice - img_slice.min())/(img_slice.max() - img_slice.min())
        value = brisq.get_score(img_slice)
        if not np.isnan(value):
            average = average + value
            valid = valid+1
    average = average/valid
    scores_average_start_affine.append(average)


########## REF START  ###############


for i in num_cts:
    input_name = input_path + str(i) + '/StartRef_PTHTRNE-0000093/' + str(i) + '_affine/out/T_template0.nii.gz'
    template = nib.load(input_name)
    templates_ref.append(np.array(template.dataobj))


for template in templates_ref:
    x, y, z = template.shape
    average = 0
    valid = 0
    for i in range(z):
        img_slice = template[:,:,i]
        #img_slice = (img_slice - img_slice.min())/(img_slice.max() - img_slice.min())
        value = brisq.get_score(img_slice)
        if not np.isnan(value):
            average = average + value
            valid = valid+1

    average = average/valid
    scores_ref_start_affine.append(average)

fig = plt.figure(figsize=(20,10))
plt.plot(num_cts, scores_average_start_affine)
fig.suptitle('Quality of Generated Template', fontsize=20)
plt.xlabel('Number of CT scans', fontsize=18)
plt.ylabel('Image Quality Index', fontsize=16)
fig.savefig('/home/users/tperciano/Dropbox/LBL_Projects/TBI_project/ClinicalCTs/Young_F/Templates/TemplateQuality.jpg')

