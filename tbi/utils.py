import logging
import logging.config
import os

logger = logging.getLogger('tbi.utils')


def use_r():
    return os.environ.get('USE_R', 'false').lower() == 'true'


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


def crate_parser(usage="%(prog)s [options] input_glob_expression output_directory"):
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    return ArgumentParser(usage=usage, formatter_class=ArgumentDefaultsHelpFormatter)


def build_convert_arg_parser():
    parser = crate_parser()
    parser.add_argument("-p", "--prefix", type=str, default="", help="prefix to output names", required=False)
    parser.add_argument("--use-dcm2niix", action="store_true", default=False, 
                        help="use dcm2niix instead dicom_series_to_nifti")
    parser.add_argument("input", type=str, help="input glob expression")
    parser.add_argument('output', type=str, help='output directory')
    return parser


def build_pre_processing_arg_parser():
    parser = crate_parser()
    parser.add_argument("-m", "--mni-file", type=str, help="mni file", required=True)
    parser.add_argument("input", type=str, help="input glob expression")
    parser.add_argument('output', type=str, help='output directory')
    return parser


def build_skull_strip_arg_parser():
    parser = crate_parser()
    parser.add_argument("-s", "--strip", type=str, default="_normalizedWarped",
                        help="pattern to strip from output name", required=False)
    parser.add_argument("-a", "--append", type=str, default="_brain",
                        help="pattern to append to output name", required=False)
    parser.add_argument("input", type=str, help="input glob expression")
    parser.add_argument('output', type=str, help='Output directory')
    return parser


def default_template_extra_args():
    defaults = '-d 3 -i 4 -g 0.2 -j 40 -c 2 -k 1 -w 1 -m 100x70x50x10 -n 1 -r 1 -s CC -t GR -b 1'
    return os.environ.get('DEFAULT_TEMPLATE_EXTRA_ARGS',  defaults)


def build_template_command_syn_average_arg_parser():
    parser = crate_parser()
    parser.add_argument("-e", "--extra-args", type=str, default=default_template_extra_args(),
                        help="extra arguments", required=False)
    parser.add_argument("input", type=str, help="input glob expression")
    parser.add_argument('output', type=str, help='output directory')
    return parser


def build_segmentation_arg_parser():
    parser = crate_parser()
    parser.add_argument("-t", "--template-file", type=str, help="template file", required=True)
    parser.add_argument("-a", "--atlas-file", type=str, help="atlas file", required=True)
    parser.add_argument("input", type=str, help="input glob expression")
    parser.add_argument('output', type=str, help='output directory')
    return parser


def build_label_geometry_measures_arg_parser():
    parser = crate_parser()
    parser.add_argument("input", type=str, help="input glob expression")
    parser.add_argument('output', type=str, help='Output directory')
    return parser


def build_image_intensify_stat_arg_parser():
    parser = crate_parser()
    parser.add_argument("-a", "--atlas-file", type=str, help="atlas file", required=True)
    parser.add_argument("input", type=str, help="input glob expression")
    parser.add_argument('output', type=str, help='output directory')
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


def replace(override_args, default_args):
    def to_dictionary(str_args):
        temp = str_args.split()

        return dict(zip(list(filter(lambda x: x.startswith('-'), temp)),
                        list(filter(lambda x: not x.startswith('-'), temp))))

    dst_dict = to_dictionary(default_args)
    dst_dict.update(to_dictionary(override_args))

    def to_string(d):
        import json

        return json.dumps(d).replace('{', '').replace(',', '').replace(':', '').replace('"', '').replace('}', '')

    return to_string(dst_dict)


def execute(cmd):
    logger.info(cmd)
    code = os.system(cmd)

    if code != 0:
        raise Exception("Failed to execute command: " + cmd)
