import logging
import os

logger = logging.getLogger('autoct.utils')

_LOGGER_SETUP = False

_err_msg_fmt = 'There were errors! (processed={}:expected={})'


def status(processed, expected):
    err, err_msg = (0, None) if processed == expected else (1, _err_msg_fmt.format(processed, expected))

    if err:
        logger.error('Done: {}'.format(err_msg))
    else:
        logger.info('Done: processed={}'.format(processed))

    return err, err_msg


def init_logger(name):
    if not _LOGGER_SETUP:
        setup_logging()

    return logging.getLogger(name)


def _get_default_level():
    return os.environ.get('AUTOCT_LOG_LEVEL', logging.INFO)


def setup_logging(level=None):
    level = level or _get_default_level()

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
                'level': level,
                'class': 'logging.StreamHandler',
                'formatter': 'detailed',
            }
        },
        'loggers': {
            'autoct': {
                'handlers': ['console'],
                'level': level,
                'propagate': True
            }
        }
    }

    import logging.config as config

    config.dictConfig(config_dict)

    global _LOGGER_SETUP

    _LOGGER_SETUP = True


def create_parser(usage='%(prog)s [options] input_glob_expression output_directory', 
                  description='', 
                  formatter_class=None):
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    formatter_class = formatter_class or RawDescriptionHelpFormatter
    return ArgumentParser(usage=usage, description=description, formatter_class=formatter_class)


def build_convert_arg_parser():
    description = (
           'Convert a series of .dcm files to .nii.gz files.'
           '\n'
           '\n'
           'Examples:'
           '\n'
           "      autoct-convert 'dcmfiles/*' convert"
           '\n'
           "      autoct-convert --use-dcm2niix 'dcmfiles/*' convert"
           '\n'
    )

    parser = create_parser(description=description)
    parser.add_argument('-p', '--prefix', type=str, default='', help='prefix to output names', required=False)
    parser.add_argument('--use-dcm2niix', action='store_true', default=False, 
                        help='use dcm2niix instead dicom_series_to_nifti')
    parser.add_argument('input', type=str, help='input glob expression')
    parser.add_argument('output', type=str, help='output directory')
    return parser


def build_pre_processing_arg_parser():
    description = (
           'Process image orientation, voxel size/resolution, bias correction and pre-alignment.'
           '\n'
           '\n'
           'Example:'
           '\n'
           "      autoct-preprocessing -m MNI152_T1_1mm_brain.nii.gz 'convert/*.nii.gz' preprocessing"
           '\n'
    )

    parser = create_parser(description=description)
    parser.add_argument('-m', '--mni-file', type=str, help='mni file', required=True)
    parser.add_argument('input', type=str, help='input glob expression')
    parser.add_argument('output', type=str, help='output directory')
    return parser


def build_bone_strip_arg_parser():
    description = (
           'Strip the bone from CT volume.'
           '\n'
           '\n'
           'Example:'
           '\n'
           "      autoct-bone-strip  'preprocessing/*.nii.gz' brains"
           '\n'
    )

    parser = create_parser(description=description)
    parser.add_argument('input', type=str, help='input glob expression')
    parser.add_argument('output', type=str, help='Output directory')
    return parser


def default_template_extra_args():
    defaults = '-d 3 -i 4 -g 0.2 -j 40 -c 2 -k 1 -w 1 -m 100x70x50x10 -n 1 -r 1 -s CC -t GR -b 1'
    return os.environ.get('DEFAULT_TEMPLATE_EXTRA_ARGS',  defaults)


def build_template_command_syn_average_arg_parser():
    description = (
           'Create template from a list of nii files.'
           '\n'
           '\n'
           'Examples:'
           '\n'
           "      autoct-template-command-syn-average 'brains/*.nii.gz' template_output"
           '\n'
           "      autoct-template-command-syn-average -e '-i 5' 'brains/*.nii.gz' template_output"
           '\n'
    )

    defaults = default_template_extra_args()
    parser = create_parser(description=description)
    parser.add_argument('-e', '--extra-args', type=str, default=defaults,
                        help='extra arguments (defaults to %s)' % defaults, required=False)
    parser.add_argument('input', type=str, help='input glob expression')
    parser.add_argument('output', type=str, help='output directory')
    return parser


def supported_registration_transforms():
    return 's', 'a', 'so'


def build_registration_arg_parser():
    description = (
           'Register the bone-stripped CT scan to a template.'
           '\n'
           '\n'
           'Supported transforms:'
           '\n'
           '        a:  rigid + affine (2 stages)'
           '\n'
           '        s:  rigid + affine + deformable syn (3 stages)'
           '\n'
           '        so: deformable syn only (1 stage) Depends on transform [a]'
           '\n'
           'Examples:'
           '\n'
           "      autoct-registration -T a so -t T_template0.nii.gz  'brains/*.nii.gz' registration"
           '\n'
           "      autoct-registration -T s -t T_template0.nii.gz  'brains/*.nii.gz' registration"
           '\n'
    )

    parser = create_parser(description=description)
    defaults = list(supported_registration_transforms())
    parser.add_argument('-T', '--transforms', nargs='+', default=defaults,
                        help='transforms to use (defaults to %s)' % defaults)
    parser.add_argument('-t', '--template-file', type=str, help='template file', required=True)
    parser.add_argument('input', type=str, help='input glob expression for bone-stripped CT scans')
    parser.add_argument('output', type=str, help='output directory')
    return parser


def supported_segmentation_types():
    return 'Affine', 'Physical'


def build_segmentation_arg_parser():
    description = (
           'Segment the registered bone-stripped CT scan based on a given atlas.'
           '\n'
           '\n'
           'Supported segmentation types:'
           '\n'
           '        Affine:   Segmentation in the transformed affine space. '
           '\n'
           '        Physical: segmentation in the pre-processed patient space'
           '\n'
           'Examples:'
           '\n'
           "    autoct-segmentation -T Physical -a New_atlas_cort_asym_sub.nii.gz 'registration/*/*.nii.gz'" 
           " segmentation"
           '\n'
           "    autoct-segmentation -T Affine, Physical -a New_atlas_cort_asym_sub.nii.gz 'registration/*/*.nii.gz'"
           " segmentation"
           '\n'
    )

    parser = create_parser(description=description)
    defaults = list(supported_segmentation_types())
    parser.add_argument('-T', '--types', nargs='+', default=defaults,
                        help='segmentation types to use (defaults to %s)' % defaults)
    parser.add_argument('-a', '--atlas-file', type=str, help='atlas file', required=True)
    parser.add_argument('input', type=str, help='input glob expression')
    parser.add_argument('output', type=str, help='output directory')
    return parser


def build_label_geometry_measures_arg_parser():
    description = (
           'Show geometric measures of the segmented regions.'
           '\n'
           '\n'
           'Example:'
           '\n'
           "      autoct-label-geometry-measures 'segmentation/*/*.nii.gz' label-geometry-measures"
           '\n'
    )

    parser = create_parser(description=description)
    parser.add_argument('input', type=str, help='input glob expression')
    parser.add_argument('output', type=str, help='Output directory')
    return parser


def build_image_intensify_stat_arg_parser():
    description = (
        'Calculate statistics of warp image for each region of the brain.'
        '\n'
        '\n'
        'Example:'
        '\n'
        "      autoct-warp_intensity_stats -a New_atlas_cort_asym_sub.nii.gz 'registration/*/*.nii.gz'"
        " warp_intensity_stats"
        '\n'
    )

    parser = create_parser(description=description)
    parser.add_argument('-a', '--atlas-file', type=str, help='atlas file', required=True)
    parser.add_argument('input', type=str, help='input glob expression')
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


def prefix(file, pattern):
    basename = os.path.basename(file)
    idx = basename.rindex(pattern)
    return basename[:idx]


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
    logger.debug(cmd)
    code = os.system(cmd)

    if code != 0:
        raise Exception('Failed to execute command: ' + cmd)
