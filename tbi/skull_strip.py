import os
from glob import glob

import nibabel as nib

from . import utils
from .fsl import fsl_skull_strip
from .image_utils import rescale, calibrate_image


def skull_strip_using_py(argv):
    import tempfile

    logger = utils.init_logger('tbi.skull_strip', True)
    parser = utils.build_skull_strip_arg_parser()
    args = parser.parse_args(argv)
    logger.info('Arguments: {0}'.format(args))

    os.makedirs(args.output, exist_ok=True)

    files = glob(args.input)
    files.sort()
    logger.debug('Processing files {0}'.format(files))
    os.makedirs(args.output, exist_ok=True)
    temp_dir = tempfile.TemporaryDirectory()

    for file in files:
        logger.info('Processing file {0}'.format(file))
        file_name = os.path.basename(file)
        temp_file = os.path.join(temp_dir.name, 'temp.nii')
        logger.info('Using temp file {0}'.format(temp_file))
        img = nib.load(file)
        logger.info('Rescaling image @ {0}'.format(file))
        rescale(img)
        logger.info('Calibrating image @ {0}'.format(file))
        calibrate_image(img)
        nib.save(img, temp_file)
        idx = file_name.index(args.strip)
        output = os.path.join(args.output, file_name[0:idx] + args.append + '.nii.gz')
        logger.info('Using output {0}'.format(output))
        img = fsl_skull_strip(temp_file, temp_dir.name)
        calibrate_image(img)
        nib.save(img, output)

    logger.info('Done')


def skull_strip_using_r(argv):
    logger = utils.init_logger('tbi.skull_strip', True)
    parser = utils.build_skull_strip_arg_parser()
    args = parser.parse_args(argv)
    logger.info('Arguments: {0}'.format(args))

    script = utils.locate_script(__file__, 'skull_strip.R')
    logger.info('Using R script at {0}'.format(script))
    os.makedirs(args.output, exist_ok=True)

    files = glob(args.input)
    files.sort()

    logger.debug('Processing files {0}'.format(files))
    os.makedirs(args.output, exist_ok=True)

    for file in files:
        logger.info('Processing file {0}'.format(file))
        utils.execute('Rscript {0} {1} {2} {3} {4}'.format(script, file, args.output, args.strip, args.append))

    logger.info('Done')


def skull_strip(argv):
    if utils.use_r():
        skull_strip_using_r(argv)
    else:
        skull_strip_using_py(argv)


def main():
    import sys

    skull_strip(sys.argv[1:])


if __name__ == '__main__':
    main()
