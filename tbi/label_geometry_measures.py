import os
from glob import glob
from subprocess import call

from . import utils


def sort_key_func(s):
    return os.path.basename(s).split('/')[-1][:7]


def main():
    logger = utils.init_logger('tbi.label_geometry_measures', True)
    parser = utils.build_label_geometry_measures_arg_parser()
    args = parser.parse_args()
    file_names = glob(args.input)
    file_names.sort(key=sort_key_func)
    logger.debug('Found files {0}'.format(file_names))

    for file_name in file_names:
        output_name = file_name.split('/')[-1][:7]
        logger.info("Processing file name:  {0}".format(output_name))
        call(['LabelGeometryMeasures', '3', file_name])


if __name__ == '__main__':
    main()
