import os

from glob import glob

from . import utils

logger = utils.init_logger('tbi.skull_strip')


__suffix = '_brain.nii.gz'
__expected_pattern = '_normalizedWarped.nii'


def skull_strip(pattern, out_dir):
    """Strip the skull from CT volume.

    Parameters
    ----------
        pattern : str
            Glob path expression to locate the CT volume
        out_dir  : str
            Output directory
    """
    import nibabel as nib
    import tempfile

    from .fsl import fsl_skull_strip
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
            out_file = os.path.join(out_dir, utils.prefix(file, __expected_pattern) + __suffix)
            img = fsl_skull_strip(temp_file, temp_dir.name)
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
    parser = utils.build_skull_strip_arg_parser()
    args = parser.parse_args(argv)
    code, _ = skull_strip(args.input, args.output)
    sys.exit(code)
