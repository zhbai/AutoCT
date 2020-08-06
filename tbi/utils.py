import logging
import logging.config
import os

from argparse import ArgumentParser


def init_logger(name, setup=False):
    if setup:
        setup_logging()

    return logging.getLogger(name)


def _get_default_level():
    return os.environ.get('TBI_LOG_LEVEL', logging.INFO)


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
                'formatter': 'detailed',
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
    parser.add_argument("-i", "--input", type=str, help="input path as a glob expression", required=True)
    parser.add_argument("-m", "--mni-file", type=str, help="mni file", required=True)
    parser.add_argument('output', type=str, help='Output directory')
    return parser


def build_skull_strip_arg_parser():
    parser = ArgumentParser(usage="%(prog)s [options] output_directory")
    parser.add_argument("-i", "--input", type=str, help="input path as a glob expression", required=True)
    parser.add_argument('output', type=str, help='Output directory')
    return parser


def build_template_command_syn_average_arg_parser():
    parser = ArgumentParser(usage="%(prog)s [options] output_directory")
    parser.add_argument("-l", "--iteration-limit", type=int, default=4, help="iterations of the template construction", required=False)
    parser.add_argument("-j", "--cpu-cores", type=int, default=40, help="number of cpu cores to use", required=False)
    parser.add_argument("-m", "--max-iterations", type=str, default="100x70x50x10", help="max-iterations in each registration", required=False)
    parser.add_argument("-e", "--extra-args", type=str, default="-d 3 -g 0.2 -k 1 -w 1 -n 1 -r 1 -s CC -t GR -b 1", help="extra arguments", required=False)
    parser.add_argument("-i", "--input", type=str, help="input path", required=True)
    parser.add_argument('output', type=str, help='Output directory')
    return parser


def build_segmentation_arg_parser():
    parser = ArgumentParser(usage="%(prog)s [options] output_directory")
    parser.add_argument("-i", "--input", type=str, help="input path as a glob expression", required=True)
    parser.add_argument("-t", "--template-file", type=str, help="template file", required=True)
    parser.add_argument("-a", "--atlas-file", type=str, help="atlas file", required=True)
    parser.add_argument('output', type=str, help='Output directory')
    return parser


def build_label_geometry_measures_arg_parser():
    parser = ArgumentParser(usage="%(prog)s [options] output_directory")
    parser.add_argument("-i", "--input", type=str, help="input path as a glob expression", required=True)
    parser.add_argument('output', type=str, help='Output directory')
    return parser


def build_image_intensify_stat_jac_arg_parser():
    parser = ArgumentParser(usage="%(prog)s [options] output_directory")
    parser.add_argument("-i", "--input", type=str, help="input path as a glob expression", required=True)
    parser.add_argument("-t", "--template-file", type=str, help="template file", required=True)
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


def locate_script(python_path, script_name):
    dir_path = os.path.dirname(os.path.realpath(python_path))
    return os.path.join(dir_path, script_name)
