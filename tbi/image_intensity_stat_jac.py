import os
from glob import glob
from subprocess import call

from . import utils


def main():
    logger = utils.init_logger('tbi.image_intensify_stat_jac', True)
    parser = utils.build_image_intensify_stat_jac_arg_parser()
    args = parser.parse_args()

    file_names = glob(args.input)
    logger.debug('Found files {0}'.format(file_names))
    template = args.template_file

    os.makedirs(args.output, exist_ok=True)

    for file_name in file_names:
        logger.info("Processing file name:  {0}".format(file_name))
        output_name = os.path.basename(file_name)
        idx = output_name.rindex('.nii')
        output_name = output_name[:idx]
        output = os.path.join(args.output, output_name + '.txt')
        logger.info("Saving to file name: {0}".format(output))
        os.system('ImageIntensityStatistics {0} {1} {2} > {3}'.format(3, file_name, template, output))


if __name__ == '__main__':
    main()
