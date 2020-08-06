#!/usr/bin/env python
# coding: utf-8

# In[1]:


from tbi.convert import convert
from tbi.preprocessing import preprocessing
from tbi.skull_strip import skull_strip
from tbi.segmentation import segmentation
from tbi.label_geometry_measures import label_geometry_measures
from tbi.image_intensity_stat_jac import image_intensity_stat_jac

from glob import glob
from nilearn.plotting import plot_img
from os.path import join

import os


# In[2]:


dcmfiles = '/data/BR-1001/*/*/'
convert_prefix = 'BR1001'
output = '/data/out'
mni_file = '/data/MNI152_T1_1mm_brain.nii'
atlas_file = '/data/New_atlas_cort_asym_sub.nii.gz'
template_file = '/data/TemplateYoungM_128.nii.gz'


# In[3]:


convert_dir = join(output, 'convert')
convert_args = ['-i', 
                dcmfiles, 
                '-p',
                convert_prefix,
                convert_dir
               ]
convert(convert_args)


# In[4]:


nii_files = os.listdir(convert_dir)

for nii_file in nii_files:
    print('Plotting {0}'.format(nii_file))
    plot_img(join(convert_dir, nii_file))


# In[5]:


preprocessing_dir = join(output, 'preprocessing')
preprocessing_args = ['-i', 
                      join(convert_dir, '*.nii'), 
                      '-m', 
                      mni_file, 
                      preprocessing_dir
                     ]
preprocessing(preprocessing_args)


# In[6]:


nii_files = os.listdir(preprocessing_dir)

for nii_file in nii_files:
    if nii_file.endswith(".nii.gz"):
        print('Plotting {0}'.format(nii_file))
        plot_img(join(preprocessing_dir, nii_file))
        


# In[7]:


skull_strip_dir = join(output, 'skull_strip')
skull_strip_args = ['-i', 
                    join(preprocessing_dir, '*_normalizedWarped.nii.gz'),
                    skull_strip_dir
                   ]
skull_strip(skull_strip_args)


# In[8]:


nii_files = os.listdir(skull_strip_dir)

for nii_file in nii_files:
    print('Plotting {0}'.format(nii_file))
    plot_img(join(skull_strip_dir, nii_file))


# In[9]:


skulls = join(skull_strip_dir, '*_brain.nii.gz')
segmentation_dir = join(output, 'segmentation')
segmentation_args = ['-i', 
                     skulls, 
                     '-t', template_file, 
                     '-a', 
                     atlas_file, 
                     segmentation_dir
                    ]
segmentation(segmentation_args)


# In[10]:


nii_files = glob(join(segmentation_dir, 'SEG/*/*.nii.gz'))
for nii_file in nii_files:
    print(nii_file)
    plot_img(nii_file)


# In[11]:


nii_files = glob(join(segmentation_dir, 'REGIS/Affine2SyN/*affine2Syn1Warp.nii.gz'))
for nii_file in nii_files:
    print(nii_file)
    #Need to figure out how to plot this 5 dimension image
    #plot_img(nii_file)


# In[12]:


label_geometry_measures_dir = join(output, 'label_geometry_measures')
label_geometry_measures_args = ['-i', 
                                join(segmentation_dir, 'SEG/*/*.nii.gz'),
                                label_geometry_measures_dir
                               ]
label_geometry_measures(label_geometry_measures_args)


# In[13]:


image_intensity_stat_jac_dir = join(output, 'image_intensity_stat_jac')

image_intensity_stat_jac_args = ['-i', 
                                 join(segmentation_dir, 'REGIS/Affine2SyN/*affine2Syn1Warp.nii.gz'), 
                                 '-a',
                                 atlas_file,
                                 image_intensity_stat_jac_dir
                                ]

image_intensity_stat_jac(image_intensity_stat_jac_args)

