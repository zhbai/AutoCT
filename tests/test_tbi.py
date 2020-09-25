import pytest

from tbi import utils
from tbi.template_command_syn_average import syn_average

import tbi.skull_strip as tbisp 

from . import input_dir, output_dir 

def test_skull_strip():
    input_file = input_dir('ID_0ead008d-ecef2edb6b_normalizedWarped.nii.gz')
    args = [input_file, output_dir('brains')]
    tbisp.nii_extension = '.nii'
    tbisp.skull_strip(args)
    output_file  = output_dir('brains', 'ID_0ead008d-ecef2edb6b_brain.nii')

    # File generate using R code
    expected = input_dir('expected', 'skull_strip', 'ID_0ead008d-ecef2edb6b_brain.nii')

    cmd = 'diff {0} {1}'.format(expected, output_file)
    utils.execute(cmd) 


#@pytest.fixture
#@pytest.mark.usefixtures('test_skull_strip')
#def test_template():
#    extra_args = '-i 1 -j 4 -m 1x1x1x1'
#    args = ['-e', extra_args, input_dir('skulls/*.nii.gz'), output_dir('template')]
#    syn_average(args)
