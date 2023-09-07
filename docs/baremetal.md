# AutoCT

## Installing Development Mode

### Required Software
    - Python (3.7)
    - ANTs (2.3.1)
    - FSL (5.0.10)

#### AutoCT Repository:

Clone the `AutoCT` repository.

```sh
git clone https://github.com/zhbai/AutoCT.git
cd AutoCT
```


#### Installation Using Conda:

```sh
conda create -n my-autoct python=3.7
conda activate my-autoct
python -m pip install .
# For devolopment mode 
python -m pip install -e .
```

### Run Tools
```sh
## Workflow tools:
autoct-convert -h
autoct-preprocessing -h
autoct-bone-strip -h
autoct-registration -h
autoct-segmentation -h
autoct-label-geometry-measures -h 
autoct-warp-intensity-stats -h

## Template tools:
autoct-template-command-syn-average -h 
```

### Example Workflow using illustration data.

The following commands allow you to run all the workflow steps. 

```sh
## Inside container:
mkdir output
autoct-convert --use-dcm2niix 'notebooks/illustration_data/dcmfiles/*' output

autoct-preprocessing -m notebooks/illustration_data/MNI152_T1_1mm_brain.nii.gz 'output/*/convert/*.nii.gz' output

autoct-bone-strip 'output/*/preprocessing/*.nii.gz' output

autoct-registration -t notebooks/illustration_data/T_template0.nii.gz 'output/*/bone_strip/*.nii.gz' output

autoct-segmentation -a notebooks/illustration_data/New_atlas_cort_asym_sub.nii.gz 'output/*/registration/*/*.nii.gz' output

autoct-label-geometry-measures 'output/*/segmentation/*/*.nii.gz' output

autoct-warp-intensity-stats -a notebooks/illustration_data/New_atlas_cort_asym_sub.nii.gz \
   'output/*/registration/*/*.nii.gz'output
```

### Running Example Jupyter Notebook

```sh
cd notebooks
jupyter nbextension enable --py widgetsnbextension
jupyter notebook notebooks/
```
### Running Tests:
```sh
python -m pip install -e .
pytest tests
```
