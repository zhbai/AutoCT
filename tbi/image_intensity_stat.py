import os
import pandas as pd
import sys

from glob import glob

from . import utils

logger = utils.init_logger('tbi.image_intensity_stat')


def image_intensity_stat(pattern, output, atlas):
    file_names = glob(pattern)
    logger.debug('Found files {}'.format(file_names))

    os.makedirs(output, exist_ok=True)

    for file_name in file_names:
        logger.info("Processing file name:  {}".format(file_name))
        output_name = os.path.basename(file_name)
        idx = output_name.rindex('.nii')
        output_name = output_name[:idx]
        txt_file = os.path.join(output, output_name + '.txt')
        logger.info("Saving to file name: {}".format(txt_file))
        utils.execute('ImageIntensityStatistics {} {} {} > {}'.format(3, file_name, atlas, txt_file))
        df = pd.read_csv(txt_file, sep=' +', engine='python', index_col=0)
        csv_file = os.path.join(output, output_name + '.csv')
        logger.info("Saving to csv file name: {}".format(csv_file))
        df.to_csv(csv_file, encoding='utf-8')

    logger.info('Done')


def main(argv=sys.argv[1:]):
    parser = utils.build_image_intensify_stat_arg_parser()
    args = parser.parse_args(argv)
    logger.info('Arguments {}'.format(args))
    image_intensity_stat(args.input, args.output, args.atlas_file)


if __name__ == '__main__':
    main(sys.argv[1:])
