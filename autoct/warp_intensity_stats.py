import os
import pandas as pd

from glob import glob

from . import utils

logger = utils.init_logger('autoct.warp_intensity_stats')

__expected_pattern = '_preprocessed_affine2Syn1Warp.nii'


def warp_intensity_stats(pattern, out_dir, atlas):
    """Calculate statistics of warp image for each region of the brain.

     Parameters
     ----------
         pattern : str
             Glob path expression to locate the warp image
         out_dir  : str
             Output directory
         atlas: str
             Path to atlas file
     """
    logger.info('Arguments {}:{}:{}'.format(pattern, out_dir, atlas))

    if not os.path.isfile(atlas or ''):
        err_msg = 'Did not find atlas file {}'.format(atlas)
        logger.error(err_msg)
        return -1, err_msg

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

    count = 0
    logger.info('Found {} files'.format(num_files))

    for file in files:
        try:
            logger.info('Processing {}'.format(file))
            output_name = utils.prefix(file, '.nii')
            prefix = utils.prefix(file, __expected_pattern)
            intensity_stats_dir = os.path.join(out_dir, prefix, 'warp_intensity_stats')
            os.makedirs(intensity_stats_dir, exist_ok=True)
            txt_file = os.path.join(intensity_stats_dir, output_name + '.txt')
            utils.execute('ImageIntensityStatistics {} {} {} > {}'.format(3, file, atlas, txt_file))
            df = pd.read_csv(txt_file, sep=' +', engine='python', index_col=0)
            csv_file = os.path.join(intensity_stats_dir, output_name + '.csv')
            df.to_csv(csv_file, encoding='utf-8')
            logger.info("Saved to csv file name: {}".format(csv_file))
            count += 1
        except Exception as ex:
            logger.warning('Processing {} encountered exception {}'.format(file, ex))

    return utils.status(count, num_files)


def main(argv=None):
    import sys

    argv = argv or sys.argv[1:]
    parser = utils.build_image_intensify_stat_arg_parser()
    args = parser.parse_args(argv)
    code, _ = warp_intensity_stats(args.input, args.output, args.atlas_file)
    sys.exit(code)
