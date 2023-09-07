import os

from glob import glob

from . import utils

logger = utils.init_logger('autoct.registration')

__expected_pattern = '_brain.nii'
__dir_names = {'s': 'SyN', 'a': 'Affine', 'so': 'Affine2SyN'}
__labels = {'s': 'SyN', 'a': 'affine', 'so': 'affine2Syn'}


def __registration(file, out_dir, template, transform):
    logger.info('Processing {}:{}'.format(transform, file))
    output_name = utils.prefix(file, __expected_pattern)

    registration_dir = os.path.join(out_dir, output_name, 'registration')
    out_file = os.path.join(registration_dir,
                            __dir_names[transform],
                            output_name + '_preprocessed_' + __labels[transform])
    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    if transform == 'so':
        warp_file = os.path.join(registration_dir,
                                 __dir_names['a'],
                                 output_name + '_preprocessed_' + __labels['a'] + 'Warped.nii.gz')

        if not os.path.isfile(warp_file):
            logger.warning('Did not find matching affine warp file {}'.format(warp_file))
            return False

        target_file = warp_file
    else:
        target_file = file

    fmt = '{} -d 3 -n 4 -f {} -m {} -o {} -t {}'
    cmd = 'antsRegistrationSyNQuick.sh'
    utils.execute(fmt.format(cmd, template, target_file, out_file, transform))
    logger.info('Saved to {}'.format(out_file))
    return True


def registration(pattern, out_dir, template, transforms=None):
    """Register the bone-stripped CT scan to a template.

    Supported transforms:
        a:  rigid + affine (2 stages)'
        s:  rigid + affine + deformable syn (3 stages)'
        so: deformable syn only (1 stage) Depends on transform [a]'

    Parameters
    ----------
        pattern : str
            Glob path expression to locate the bone-stripped CT scan
        out_dir  : str
            Output Directory
        template: str 
            Path to template file
        transforms: list, optional 
            List of transforms (default to ['a', 's', 'so'])
    """
    logger.info('Arguments: {}:{}:{}:{}'.format(pattern, out_dir, template, transforms))

    if not os.path.isfile(template or ''):
        err_msg = 'Did not find template file {}'.format(template)
        logger.error(err_msg)
        return -1, err_msg

    defaults = utils.supported_registration_transforms()
    transforms = transforms or defaults
    transforms = set(transforms)

    if not transforms.issubset(defaults):
        err_msg = "Unsupported transform(s) :{}".format(transforms)
        logger.error(err_msg)
        return -1, err_msg

    files = [file for file in glob(pattern or '') if __expected_pattern in os.path.basename(file)]
    num_files = len(files)

    if not num_files:
        err_msg = 'Did not find any file with expected pattern {}'.format(__expected_pattern)
        logger.error(err_msg)
        return -1, err_msg

    try:
        os.makedirs(out_dir, exist_ok=True)
    except Exception as ex:
        err_msg = 'Error creating directory {}'.format(ex)
        logger.error(err_msg)
        return -1, err_msg

    count = 0
    logger.info('Found {} files'.format(num_files))

    for file in files:
        for transform in sorted(transforms):
            try:
                if __registration(file, out_dir, template, transform):
                    count += 1
            except Exception as ex:
                logger.warning('Processing {} encountered exception {}'.format(file, ex))

    return utils.status(count, num_files * len(transforms))


def main(argv=None):
    import sys

    argv = argv or sys.argv[1:]
    parser = utils.build_registration_arg_parser()
    args = parser.parse_args(argv)
    code, _ = registration(args.input, args.output, args.template_file, args.transforms)
    sys.exit(code)
