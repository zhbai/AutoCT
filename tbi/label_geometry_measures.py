import os
from glob import glob
from subprocess import call

from . import utils


def main():
    logger = utils.init_logger('tbi.label_geometry_measures', True)
    parser = utils.build_label_geometry_measures_arg_parser()
    args = parser.parse_args()
    file_names = glob(args.input)
    logger.debug('Found files {0}'.format(file_names))

    os.makedirs(args.output, exist_ok=True)

    for file_name in file_names:
        logger.info("Processing file name:  {0}".format(file_name))
        output_name = os.path.basename(file_name) 
        idx = output_name.rindex('.nii')
        output_name = output_name[:idx]
        output = os.path.join(args.output, output_name + '.txt')
        logger.info("Saving to file name: {0}".format(output))
        os.system('LabelGeometryMeasures {0} {1} > {2}'.format(3, file_name, output))


if __name__ == '__main__':
    main()
