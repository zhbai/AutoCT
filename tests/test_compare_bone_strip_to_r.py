import os.path
import pytest

import autoct


def input_dir():
    _data_dir = 'testdata'
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, _data_dir)


def output_dir():
    _output_dir = 'output'
    dir_path = '/tmp'
    return os.path.join(dir_path, _output_dir)


def compare_images(img1, img2):
    import nibabel as nib
    import numpy as np
    
    img1 = nib.load(img1)
    img2 = nib.load(img2)
    comp = img1.get_fdata() ==  img2.get_fdata()
    return comp.all() and img1.header == img2.header


def bone_strip_filename():
    return 'ID_0ead008d-ecef2edb6b_brain.nii.gz'


@pytest.fixture
def bone_strip_input():
    return os.path.join(input_dir(), 'ID_0ead008d-ecef2edb6b_normalizedWarped.nii.gz')


def test_bone_strip(bone_strip_input):
    autoct.bone_strip(bone_strip_input, output_dir())

    # File generated using R code
    bone_strip_expected = os.path.join(input_dir(), 'expected', 'bone_strip', bone_strip_filename())

    from autoct import utils

    prefix = utils.prefix(bone_strip_input, '_normalizedWarped.nii')
    bone_strip_output_file = os.path.join(output_dir(), 
                                           prefix, 
                                           'bone_strip', 
                                           bone_strip_filename())
    assert compare_images(bone_strip_expected, bone_strip_output_file)
