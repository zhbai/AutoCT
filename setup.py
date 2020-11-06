from setuptools import setup, find_packages

setup(
    name='autoct_registration',
    version='0.1.0',
    include_package_data=True,
    url='https://bitbucket.org/LBL_TBI/tbi_registration/',
    author='Zhe Bai, Abdelilah Essiari',
    author_email='zhebai@lbl.gov, aessiari@lbl.gov',
    description='Description of my package',
    packages=find_packages(),    
    install_requires=[
       'dicom2nifti==2.0.9', 
       'nibabel==3.2.0', 
       'nilearn==0.6.2', 
       'pytest==6.0.1', 
       'matplotlib==3.0.3', 
       'pandas==1.1.2',
       'notebook==6.1.4',
       'ipywidgets==7.5.1',
    ],
    entry_points={
       'console_scripts': [
              'autoct-convert = autoct.convert:main',
              'autoct-preprocessing = autoct.preprocessing:main',
              'autoct-skull-strip = autoct.skull_strip:main',
              'autoct-template-command-syn-average = autoct.template_command_syn_average:main',
              'autoct-registration = autoct.registration:main',
              'autoct-segmentation = autoct.segmentation:main',
              'autoct-warp-intensity-stats = autoct.warp_intensity_stats:main',
              'autoct-label-geometry-measures = autoct.label_geometry_measures:main'
       ]
    },
)
