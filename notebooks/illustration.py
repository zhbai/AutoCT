#!/usr/bin/env python
# coding: utf-8

# In[16]:


from tbi.segmentation import segmentation
from tbi.label_geometry_measures import label_geometry_measures
from tbi.image_intensity_stat_jac import image_intensity_stat_jac
from tbi.skull_strip import skull_strip
from tbi.preprocessing import preprocessing

from glob import glob
from nilearn.plotting import plot_img
import nilearn.plotting as plotting
import pandas as pd
from os.path import join
from IPython.display import display


# In[17]:


output = '/data/illustration/py-out3'
mni_file = 'illustration_data/MNI152_T1_1mm_brain.nii'
atlas_file = 'illustration_data/New_atlas_cort_asym_sub.nii.gz'
template_file = 'illustration_data/T_template0.nii.gz'
convert_dir = 'illustration_data/convert'


# In[18]:


preprocessing_dir = join(output, 'preprocessing')
preprocessing_args = ['-m', 
                      mni_file, 
                      join(convert_dir, '*.nii.gz'), 
                      preprocessing_dir
                     ]
preprocessing(preprocessing_args)


# In[19]:


nii_files = glob(join(preprocessing_dir, "*.nii.gz"))

for nii_file in nii_files:
    print('Plotting {0}'.format(nii_file))
    plot_img(nii_file)
    plotting.show()


# In[20]:


skull_strip_dir = join(output, 'brains')
skull_strip_args = [join(preprocessing_dir, '*_normalizedWarped.nii.gz'),
                    skull_strip_dir
                   ]
skull_strip(skull_strip_args)


# In[21]:


nii_files = glob(join(skull_strip_dir, "*.nii.gz"))

for nii_file in nii_files:
    print('Plotting {0}'.format(nii_file))
    plot_img(nii_file)
    plotting.show()


# In[22]:


brains = join(skull_strip_dir, '*.nii.gz')
segmentation_dir = join(output, 'segmentation')
segmentation_args = ['-t', 
                     template_file, 
                     '-a', 
                     atlas_file, 
                     brains, 
                     segmentation_dir
                    ]

segmentation(segmentation_args)


# In[23]:


nii_files = glob(join(segmentation_dir, 'SEG/*/*.nii.gz'))
for nii_file in nii_files:
    print(nii_file)
    plot_img(nii_file)
    plotting.show()


# In[24]:


label_geometry_measures_dir = join(output, 'label_geometry_measures')
label_geometry_measures_args = [join(segmentation_dir, 'SEG/*/*.nii.gz'),
                                label_geometry_measures_dir
                               ]

label_geometry_measures(label_geometry_measures_args)


# In[25]:


txt_files = glob(join(label_geometry_measures_dir, "*.txt"))
names='Label,Volume(voxels),SurfArea(mm^2), Eccentricity, Elongation, Orientation,Centroid, Axes Length, Bounding Box'

for txt_file in txt_files:
    print('Displaying {0}'.format(txt_file))
    df = pd.read_csv(txt_file, 
        sep=r' {2,}', 
        engine='python', 
        index_col=0, skiprows=[0], header=None, names=names.split(','))
    display(df)


# In[26]:


image_intensity_stat_jac_dir = join(output, 'image_intensity_stat_jac')
image_intensity_stat_jac_args = ['-a',
                                 atlas_file,
                                 join(segmentation_dir, 'REGIS/Affine2SyN/*affine2Syn1Warp.nii.gz'), 
                                 image_intensity_stat_jac_dir
                                ]

image_intensity_stat_jac(image_intensity_stat_jac_args)


# In[27]:


txt_files = glob(join(image_intensity_stat_jac_dir, "*.txt"))
names='Label,Volume(voxels),SurfArea(mm^2), Eccentricity, Elongation, Orientation,Centroid, Axes Length, Bounding Box'

for txt_file in txt_files:
    print('Displaying {0}'.format(txt_file))
    df = pd.read_csv(txt_file, sep=' +', engine='python', index_col=0)
    display(df)


# In[ ]:




