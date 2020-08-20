import os

from . import utils

logger = utils.init_logger('tbi.fsl', False)


def execute(cmd):
    logger.info(cmd)
    os.system(cmd)


def fsl_maths(file, outfile, opts):
    execute('fslmaths {0} {1} {2}'.format(file, opts, outfile))
    return outfile


def fsl_threshold(file, outfile, lower=0.0, upper=100.0):
    return fsl_maths(file, outfile, '-thr {0} -uthr {1}'.format(lower, upper))


def fsl_abs(file, outfile):
    return fsl_maths(file, outfile, '-abs')


def fsl_fill(file, outfile, use_bin=True):
    if use_bin:
        return fsl_maths(file, outfile, '-bin -fillh')

    return fsl_maths(file, outfile, '-fillh')


def fsl_smooth(file, outfile, sigma=1):
    return fsl_maths(file, outfile, '-s {0}'.format(sigma))


def fsl_mask(file, outfile, mask):
    return fsl_maths(file, outfile, '-mas {0}'.format(mask))


def fsl_bet2(file, outfile, opts='-f 0.01 -v'):
    execute('bet2 {0} {1} {2}'.format(file, outfile, opts))
    return outfile


def skull_strip(input_file, output_file):
    import tempfile
    import os

    temp_dir = tempfile.TemporaryDirectory()

    # Threshold image to 0-100
    threshold_file = os.path.join(temp_dir.name, 'threshold.nii.gz')
    fsl_threshold(input_file, threshold_file)

    # Creating binary mask to re-mask after filling
    mask_file = os.path.join(temp_dir.name, 'mask1.nii.gz')
    fsl_fill(
        fsl_abs(threshold_file, os.path.join(temp_dir.name, 'abs1.nii.gz')),
        mask_file)

    # Pre-smooth image and re-mask it
    temp_output_file = threshold_file
    fsl_bet2(
        fsl_mask(
            fsl_smooth(threshold_file, temp_output_file),
            temp_output_file,
            mask_file),
        temp_output_file)

    # Using fsl_fill to fill in any holes in mask
    mask_file = os.path.join(temp_dir.name, 'mask2.nii.gz')
    fsl_fill(
        fsl_abs(temp_output_file, os.path.join(temp_dir.name, 'abs2.nii.gz')),
        mask_file)

    # Using the filled mask to mask original image
    fsl_mask(input_file, output_file, mask_file)
