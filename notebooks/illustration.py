#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tbi

from glob import glob
import nilearn.plotting as plotting
import pandas as pd
from os.path import join
from IPython.display import display


# In[3]:


output = '/data/illustration/py-out4'
mni_file = 'illustration_data/MNI152_T1_1mm_brain.nii.gz'
atlas_file = 'illustration_data/New_atlas_cort_asym_sub.nii.gz'
template_file = 'illustration_data/T_template0.nii.gz'
convert_dir = 'illustration_data/convert'


# In[4]:


preprocessing_dir = join(output, 'preprocessing')
preprocessing_args = ['-m', 
                      mni_file, 
                      join(convert_dir, '*.nii.gz'), 
                      preprocessing_dir
                     ]
tbi.preprocessing(preprocessing_args)


# In[5]:


nii_files = glob(join(preprocessing_dir, "*.nii.gz"))

for nii_file in nii_files:
    print('Plotting {0}'.format(nii_file))
    plotting.plot_img(nii_file)
    plotting.show()


# In[6]:


skull_strip_dir = join(output, 'brains')
skull_strip_args = [join(preprocessing_dir, '*_normalizedWarped.nii.gz'),
                    skull_strip_dir
                   ]
tbi.skull_strip(skull_strip_args)


# In[7]:


nii_files = glob(join(skull_strip_dir, "*.nii.gz"))

for nii_file in nii_files:
    print('Plotting {0}'.format(nii_file))
    plotting.plot_img(nii_file)
    plotting.show()


# In[8]:


brains = join(skull_strip_dir, '*.nii.gz')
segmentation_dir = join(output, 'segmentation')
segmentation_args = ['-t', 
                     template_file, 
                     '-a', 
                     atlas_file, 
                     brains, 
                     segmentation_dir
                    ]

tbi.segmentation(segmentation_args)


# In[9]:


nii_files = glob(join(segmentation_dir, 'SEG/*/*.nii.gz'))
for nii_file in nii_files:
    print(nii_file)
    plotting.plot_img(nii_file)
    plotting.show()


# In[4]:


label_geometry_measures_dir = join(output, 'label_geometry_measures')
label_geometry_measures_args = [join(segmentation_dir, 'SEG/*/*.nii.gz'),
                                label_geometry_measures_dir
                               ]

tbi.label_geometry_measures(label_geometry_measures_args)


# In[5]:


csv_files = glob(join(label_geometry_measures_dir, "*.csv"))

for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    display(df.iloc[0:115,0:5])


# In[6]:


image_intensity_stat_dir = join(output, 'image_intensity_stat')
image_intensity_stat_args = ['-a',
                                 atlas_file,
                                 join(segmentation_dir, 'REGIS/Affine2SyN/*affine2Syn1Warp.nii.gz'), 
                                 image_intensity_stat_dir
                                ]

tbi.image_intensity_stat(image_intensity_stat_args)


# In[7]:


csv_files = glob(join(image_intensity_stat_dir, "*.csv"))

for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    display(df.iloc[0:115,0:5])


# In[ ]:




