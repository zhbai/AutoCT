import os
from glob import glob

from . import utils

logger = utils.init_logger('tbi.skull_strip')


def skull_strip(pattern, output, strip='_normalizedWarped', append='_brain'):
    import nibabel as nib
    from .fsl import fsl_skull_strip
    from .image_utils import rescale_img, calibrate_img, drop_img_dim
    import tempfile


    os.makedirs(output, exist_ok=True)

    files = glob(pattern)
    files.sort()
    logger.debug('Processing files {0}'.format(files))
    os.makedirs(output, exist_ok=True)
    temp_dir = tempfile.TemporaryDirectory()

    for file in files:
        logger.info('Processing file {0}'.format(file))
        file_name = os.path.basename(file)
        temp_file = os.path.join(temp_dir.name, 'rescaled.nii')
        logger.info('Using temp file {0}'.format(temp_file))
        img = nib.load(file)
        logger.info('Dropping dimensions image @ {0}'.format(file))
        img = drop_img_dim(img)
        logger.info('Rescaling image @ {0}'.format(file))
        rescale_img(img)
        logger.info('Calibrating image @ {0}'.format(file))
        calibrate_img(img)
        nib.save(img, temp_file)
        idx = file_name.index(strip)
        output = os.path.join(output,
                              file_name[0:idx] + append + '.nii.gz')
        img = fsl_skull_strip(temp_file, temp_dir.name)
        img = drop_img_dim(img)
        calibrate_img(img)
        logger.info('Using output {0}'.format(output))
        nib.save(img, output)

    logger.info('Done')

import sys

def main(argv=sys.argv[1:]):
    parser = utils.build_skull_strip_arg_parser()
    args = parser.parse_args(argv)
    logger.info('Arguments: {0}'.format(args))

    skull_strip(args.input, args.output, args.strip, args.append)


if __name__ == '__main__':
    main(sys.argv[1:])
