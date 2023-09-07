import os

from glob import glob

from . import utils

logger = utils.init_logger('autoct.segmentation')

__mat_suffixes = {'Affine': '_preprocessed_affine2Syn0GenericAffine.mat',
                  'Physical': '_preprocessed_SyN0GenericAffine.mat'}
__out_suffixes = {'Affine': '_segmentation_cortical_affine.nii.gz',
                  'Physical': '_segmentation_cortical_phy.nii.gz'}
__dir_names = {'Affine': 'AFFINE', 'Physical': 'PHYSCi'}
__expected_patterns = {'Affine': '_preprocessed_affine2Syn1InverseWarp.nii',
                       'Physical': '_preprocessed_SyN1InverseWarp.nii'}


def __segmentation(file, out_dir, atlas, seg_type):
    logger.info('Processing {}:{}'.format(seg_type, file))
    output_name = utils.prefix(file, __expected_patterns[seg_type])
    dir_name = os.path.dirname(file)
    mat_file = os.path.join(dir_name, output_name + __mat_suffixes[seg_type])

    if not os.path.isfile(mat_file):
        logger.warning('Did not find mat file {}'.format(mat_file))
        return False

    if seg_type == 'Affine':
        affine_file = os.path.join(os.path.dirname(dir_name),
                                   'Affine',
                                   output_name + '_preprocessed_affineWarped.nii.gz')

        if not os.path.isfile(affine_file):
            logger.warning('Did not find matching warped file {}'.format(affine_file))
            return False

        reference_file = affine_file
    else:
        reference_file = file

    segmentation_dir = os.path.join(out_dir, output_name, 'segmentation')
    out_file = os.path.join(segmentation_dir, __dir_names[seg_type], output_name + __out_suffixes[seg_type])
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    transforms = '[' + mat_file + ',1] ' + file
    fmt = '{} -f 0 -d 3 -n GenericLabel[Linear] -i {} -o {} -r {} -t {}'
    cmd = 'antsApplyTransforms'
    utils.execute(fmt.format(cmd, atlas, out_file, reference_file, transforms))
    logger.info('Saved to {}'.format(out_file))
    return True


def segmentation(pattern, out_dir, atlas, types=None):
    """Segment the registered bone-stripped CT scan based on a given atlas.

    Supported segmentation types:
        Affine:  segmentaion in the transformed affine space 
        Physical:  segmentation in the pre-processed patient spac 

    Parameters
    ----------
        pattern : str
            Glob path expression to locate the registered bone-stripped CT scan
        out_dir  : str
            Output Directory
        atlas: str 
            Path to atlas file
        types: list, optional 
            List of segmentation types (default to ['Affine', 'Physical'])
    """
    logger.info('Arguments: {}:{}:{}:{}'.format(pattern, out_dir, atlas, types))

    if not os.path.isfile(atlas or ''):
        err_msg = 'Did not find atlas file {}'.format(atlas)
        logger.error(err_msg)
        return -1, err_msg

    defaults = utils.supported_segmentation_types()
    types = set(types or defaults)

    if not types.issubset(defaults):
        err_msg = "Unsupported segmentation types:{}".format(types)
        logger.error(err_msg)
        return -1, err_msg

    type_to_files = dict(zip(
        types,
        [[f for f in glob(pattern or '') if __expected_patterns[seg_type]
          in os.path.basename(f)] for seg_type in types])
    )

    num_files = sum([len(e) for e in type_to_files.values()])

    if num_files == 0:
        err_msg = 'Did not find any file with expected pattern {}'.format([
            v for k, v in __expected_patterns.items() if k in types])
        logger.error(err_msg)
        return -1,  err_msg

    try:
        os.makedirs(out_dir, exist_ok=True)
    except Exception as ex:
        err_msg = 'Error creating directory {}'.format(ex)
        logger.error(err_msg)
        return -1, err_msg

    count = 0
    logger.info('Found {} files'.format(num_files))

    for seg_type, files in type_to_files.items():
        for file in files:
            try:
                if __segmentation(file, out_dir, atlas, seg_type):
                    count += 1
            except Exception as ex:
                logger.warning('Processing {} encountered exception {}'.format(file, ex))

    return utils.status(count, num_files)


def main(argv=None):
    import sys

    argv = argv or sys.argv[1:]
    parser = utils.build_segmentation_arg_parser()
    args = parser.parse_args(argv)
    code, _ = segmentation(args.input, args.output, args.atlas_file, args.types)
    sys.exit(code)
