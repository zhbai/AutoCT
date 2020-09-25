import os

_data_dir = 'testdata'
_output_dir = 'output'


def input_dir(*paths):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, _data_dir, *paths)


def output_dir(*paths):
    dir_path = '/tmp'
    return os.path.join(dir_path, _output_dir, *paths)
