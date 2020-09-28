import os
from glob import glob

from . import utils


def image_intensity_stat_jac(argv):
    logger = utils.init_logger('tbi.image_intensity_stat_jac', True)
    parser = utils.build_image_intensify_stat_jac_arg_parser()
    args = parser.parse_args(argv)

    file_names = glob(args.input)
    logger.debug('Found files {0}'.format(file_names))
    atlas = args.atlas_file

    os.makedirs(args.output, exist_ok=True)

    for file_name in file_names:
        logger.info("Processing file name:  {0}".format(file_name))
        output_name = os.path.basename(file_name)
        idx = output_name.rindex('.nii')
        output_name = output_name[:idx]
        output = os.path.join(args.output, output_name + '.txt')
        logger.info("Saving to file name: {0}".format(output))
        utils.execute('ImageIntensityStatistics {0} {1} {2} > {3}'.format(3, file_name, atlas, output))

    logger.info('Done')


def main():
    import sys

    image_intensity_stat_jac(sys.argv[1:])


if __name__ == '__main__':
    main()
