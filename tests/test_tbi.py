from tbi.skull_strip import skull_strip
from tbi.template_command_syn_average import syn_average
from . import *

import pytest


@pytest.fixture
def test_skull_strip():
    args = ['-i', input_dir('ID*.nii.gz'), output_dir('brains')]
    skull_strip(args)


@pytest.mark.usefixtures('test_skull_strip')
def test_template():
    extra_args = '-i 1 -j 4 -m 1x1x1x1'
    args = ['-e', extra_args, input_dir('skulls/*.nii.gz'), output_dir('template')]
    syn_average(args)
