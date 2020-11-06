# TBI Registration:

## Typical Workflow
- Convert dcm files to nii.gz.
- Pre-process image orientation, voxel size/resolution, bias correction and pre-alignment.
- Strip the skull from CT volume.
- Register the skull-stripped CT scan to a given template.
- Segment the skull-stripped CT scan based on a given atlas
- Calculate geometric measures 
- Calculate statistics of warp image for each region of the brain.

![png](docs/flowchart.png)

## Getting Started
   - Build docker image and use jupyter to run illustration notebook or tbi GUI notebook.
      - Refer to [this document](./docs/docker.md) for a detailed description.
   - Running on NERSC:
      - Refer to [this document](./docs/nersc.md) for a detailed description.

# Sample Workflow Snapshots:

### Convert a series of .dcm files to .nii.gz files.


```python
tbi.convert(pattern='illustration_data/dcmfiles/*',
            out_dir=join(output, 'convert'), 
            use_dcm2niix=True)
plot_images(join(output, 'convert', "*.nii.gz"))
```

    Plotting /data/illustration_workflow_output/convert/ID_0eba6ca7-7473dee7c1.nii.gz:shape=(512, 512, 35)



    
![png](docs/output_1_1.png)
    


### Pre-process and strip the skull from CT volume.


```python
tbi.preprocessing(pattern=join(output, 'convert', '*.nii.gz'), 
                  out_dir=join(output, 'preprocessing'),
                  mni_file=mni_file)
tbi.skull_strip(pattern=join(output, 'preprocessing', '*.nii.gz'),
                out_dir=join(output, 'brains'))
plot_images(join(output, 'brains', '*.nii.gz'))
```

    Plotting /data/illustration_workflow_output/brains/ID_0eba6ca7-7473dee7c1_brain.nii.gz:shape=(182, 218, 182)



    
![png](docs/output_3_1.png)
    


### Register the skull-stripped CT scan to a template and segment the skull-stripped CT scan based on a given atlas.


```python
tbi.registration(pattern=join(output, 'brains', '*.nii.gz'), 
                 out_dir=join(output, 'registration'), 
                 template=template_file,
                 transforms=tbi.supported_registration_transforms())
tbi.segmentation(pattern=join(output, 'registration', '*/*.nii.gz'), 
                 out_dir=join(output, 'segmentation'), 
                 atlas=atlas_file,
                 types=tbi.supported_segmentation_types())
plot_images(join(output, 'segmentation', '*/*.nii.gz'))
```

    Plotting /data/illustration_workflow_output/segmentation/PHYSCi/ID_0eba6ca7-7473dee7c1_segmentation_cortical_phy.nii.gz:shape=(182, 218, 182)



    
![png](docs/output_5_1.png)
    


    Plotting /data/illustration_workflow_output/segmentation/AFFINE/ID_0eba6ca7-7473dee7c1_segmentation_cortical_affine.nii.gz:shape=(182, 218, 182)



    
![png](docs/output_5_3.png)
    

