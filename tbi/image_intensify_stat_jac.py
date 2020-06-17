import os
from glob import glob
from subprocess import call

from . import utils


def sort_key_func(s):
    return os.path.basename(s).split('/')[-1][:7]


if __name__ == '__main__':
    logger = utils.init_logger('tbi.image_intensify_stat_jac', True)
    parser = utils.build_image_intensify_stat_jac_arg_parser()
    args = parser.parse_args()

    file_names = glob(args.input)
    file_names.sort(key=sort_key_func)
    logger.debug('Found files {0}'.format(file_names))
    template = args.template_file

    for file_name in file_names:
        output_name = file_name.split('/')[-1][:7]
        logger.info("Processing file name:  {0}".format(output_name))
        call(['ImageIntensityStatistics', '3', file_name, template])
