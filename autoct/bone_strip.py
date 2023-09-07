import os

from glob import glob

from . import utils

logger = utils.init_logger('autoct.bone_strip')


__suffix = '_brain.nii.gz'
__expected_pattern = '_normalizedWarped.nii'


def bone_strip(pattern, out_dir):
    """Strip the bone from CT volume.

    Parameters
    ----------
        pattern : str
            Glob path expression to locate the CT volume
        out_dir  : str
            Output directory
    """
    import nibabel as nib
    import tempfile

    from .bone_strip_helper import do_bone_strip
    from .image_utils import rescale_img, calibrate_img, drop_img_dim

    logger.info('Arguments: {}:{}'.format(pattern, out_dir))
    files = [file for file in glob(pattern or '') if __expected_pattern in os.path.basename(file)]
    num_files = len(files)

    if not num_files:
        err_msg = 'Did not find any input file with expected pattern {}'.format(__expected_pattern)
        logger.error(err_msg)
        return -1, err_msg

    try:
        os.makedirs(out_dir, exist_ok=True)
    except Exception as ex:
        err_msg = 'Error creating directory {}'.format(ex)
        logger.error(err_msg)
        return -1, err_msg

    temp_dir = tempfile.TemporaryDirectory()
    count = 0
    logger.info('Found {} files'.format(num_files))

    for file in files:
        try:
            logger.info('Processing file {}'.format(file))
            img = nib.load(file)
            logger.debug('Rescaling image at {}'.format(file))
            img = drop_img_dim(img)
            rescale_img(img)
            calibrate_img(img)
            temp_file = os.path.join(temp_dir.name, 'rescaled.nii.gz')
            nib.save(img, temp_file)
            prefix = utils.prefix(file, __expected_pattern)
            bone_strip_dir = os.path.join(out_dir, prefix, 'bone_strip')
            os.makedirs(bone_strip_dir, exist_ok=True)
            out_file = os.path.join(bone_strip_dir, prefix + __suffix)
            img = do_bone_strip(temp_file, temp_dir.name)
            img = drop_img_dim(img)
            calibrate_img(img)
            nib.save(img, out_file)
            logger.info('Saved to {}'.format(out_file))
            count += 1
        except Exception as ex:
            logger.warning('Processing {} encountered exception {}'.format(file, ex))

    return utils.status(count, num_files)


def main(argv=None):
    import sys

    argv = argv or sys.argv[1:]
    parser = utils.build_bone_strip_arg_parser()
    args = parser.parse_args(argv)
    code, _ = bone_strip(args.input, args.output)
    sys.exit(code)
