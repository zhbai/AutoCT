import logging
import logging.config
import os

from argparse import ArgumentParser


def init_logger(name,setup=False):
    if setup:
       setup_logging()

    return logging.getLogger(name)


def _get_default_level():
    return os.environ.get('TBI_LOG_LEVEL', logging.DEBUG)


def setup_logging():
    default_level = _get_default_level()

    config_dict = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'concise': {
                'format': '[%(levelname)s] %(name)s :: %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': default_level,
                'class': 'logging.StreamHandler',
                'formatter': 'concise',
            }
        },
        'loggers': {
            'tbi': {
                'handlers': ['console'],
                'level': default_level,
                'propagate': True
            }
        }
    }

    logging.config.dictConfig(config_dict)


def build_convert_arg_parser():
    parser = ArgumentParser(usage="%(prog)s [options] output_directory")
    parser.add_argument("-i", "--input", type=str, help="input path as a glob expression", required=True)
    parser.add_argument('output', type=str, help='Output directory')
    return parser


def build_pre_processing_arg_parser():
    parser = ArgumentParser(usage="%(prog)s [options] output_directory")
    parser.add_argument("-i", "--input", type=str, help="input path", required=True)
    parser.add_argument("-m", "--mni-file", type=str, help="mni file", required=True)
    parser.add_argument('output', type=str, help='Output directory')
    return parser


pathin = '/home/users/tperciano/Dropbox/LBL_Projects/TBI_project/ClinicalCTs/Young_M/Preprocessed/'
pathout = '/home/users/tperciano/Dropbox/LBL_Projects/TBI_project/ClinicalCTs/Young_M/Brains/'

def build_skull_strip_arg_parser():
    parser = ArgumentParser(usage="%(prog)s [options] output_directory")
    parser.add_argument("-i", "--input", type=str, help="input path to pre processed file", required=True)
    parser.add_argument('output', type=str, help='Output directory')
    return parser

def init_dicom2nifti_settings():
    import dicom2nifti.settings as settings

    settings.disable_validate_orthogonal()
    settings.disable_validate_sliceincrement()
    settings.disable_validate_orientation()
    settings.enable_resampling()
    settings.set_resample_spline_interpolation_order(1)
    settings.set_resample_padding(-1000)

