from setuptools import setup, find_packages

setup(
    name='tbi_registration',
    version='0.1.0',
    include_package_data=True,
    url='https://bitbucket.org/LBL_TBI/tbi_registration/',
    author='Author Name',
    author_email='author@gmail.com',
    description='Description of my package',
    packages=find_packages(),    
    install_requires=[
       'dicom2nifti==2.0.9'
    ],
    entry_points={
       'console_scripts': [
              'tbi-convert = tbi.convert:main',
              'tbi-preprocessing = tbi.preprocessing:main',
              'tbi-skull-strip = tbi.skull_strip:main',
              'tbi-template-command-syn-average = tbi.template_command_syn_average:main',
              'tbi-segmentation = tbi.segmentation:main',
              'tbi-image-intensity-stat-jac = tbi.image_intensity_stat_jac:main',
              'tbi-label-geometry-measures = tbi.label_geometry_measures:main'
       ]
    },
)
