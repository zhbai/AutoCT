import os
import pandas as pd

from glob import glob

from . import utils

logger = utils.init_logger('autoct.label_geometry_measures')

__expected_patterns = ['_segmentation_cortical_affine.nii', '_segmentation_cortical_phy.nii']
__prefix_pattern = '_segmentation_cortical_'


def label_geometry_measures(pattern, out_dir):
    """Show geometric measures of the segmented regions.

    Parameters
    ----------
        pattern : str
            Glob path expression to locate the CT volume
        out_dir  : str
            Output directory
    """
    logger.info('Arguments {}:{}'.format(pattern, out_dir))

    import functools
    import operator

    files = functools.reduce(
        operator.iconcat,
        [[f for f in glob(pattern or '') if p in os.path.basename(f)] for p in __expected_patterns], [])

    num_files = len(files)

    if not num_files:
        err_msg = 'Did not find any input file with pattern {}'.format(__expected_patterns)
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
    names = 'Label,Volume(voxels),SurfArea(mm^2),Eccentricity,Elongation,Orientation,Centroid,Axes Length,Bounding Box'

    for file in files:
        try:
            logger.info("Processing file name:  {}".format(file))
            output_name = utils.prefix(file, '.nii')
            prefix = utils.prefix(output_name, __prefix_pattern)
            geometry_measures_dir = os.path.join(out_dir, prefix, 'label_geometry_measures')
            os.makedirs(geometry_measures_dir, exist_ok=True)
            txt_file = os.path.join(geometry_measures_dir, output_name + '.txt')
            logger.info("Saving to file name: {}".format(txt_file))
            utils.execute('LabelGeometryMeasures {} {} > {}'.format(3, file, txt_file))
            df = pd.read_csv(txt_file,
                             sep=r' {2,}',
                             engine='python',
                             index_col=0, skiprows=[0], header=None, names=names.split(','))

            csv_file = os.path.join(geometry_measures_dir, output_name + '.csv')
            logger.info("Saving to csv file name: {}".format(csv_file))
            df.to_csv(csv_file, encoding='utf-8')
            count += 1
        except Exception as ex:
            logger.warning('Processing {} encountered exception {}'.format(file, ex))

    return utils.status(count, num_files)


def main(argv=None):
    import sys

    argv = argv or sys.argv[1:]

    parser = utils.build_label_geometry_measures_arg_parser()
    args = parser.parse_args(argv)
    code, _ = label_geometry_measures(args.input, args.output)
    sys.exit(code)
