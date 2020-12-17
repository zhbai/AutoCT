import dicom2nifti
import os

from glob import glob

from . import utils

logger = utils.init_logger('autoct.convert')


def convert(pattern, out_dir, prefix='', use_dcm2niix=False):
    """Convert dcm files to nii.

    Parameters
    ----------
        pattern : str
            Glob path expression to locate dcm folders
        out_dir  : str
            Output directory
        prefix: str, optional
            Can be used prefix all output files when using same top level directory
        use_dcm2niix: bool
            Whether to use dcm2niix tool. (default to False)
    """
    logger.info('Arguments: {}:{}'.format(pattern, out_dir))
    utils.init_dicom2nifti_settings()

    folders = glob(pattern or '')
    logger.debug('Processing folders {}'.format(folders))

    num_folders = len(folders)

    if not num_folders:
        err_msg = 'Did not find any input file with expected pattern {}'.format(pattern)
        logger.error(err_msg)
        return -1, err_msg

    try:
        os.makedirs(out_dir, exist_ok=True)
    except Exception as ex:
        err_msg = 'Error creating directory {}'.format(ex)
        logger.error(err_msg)
        return -1, err_msg

    os.makedirs(out_dir, exist_ok=True)
    count = 0

    for folder in folders:
        logger.info('Processing folder {}'.format(folder))

        if folder.endswith('/'):
            output_name = os.path.basename(os.path.dirname(folder))
        else:
            output_name = os.path.basename(folder)

        output_name = output_name.replace(' ', '_')
        output_name = output_name.replace('.', '_')

        if prefix:
            output_name = prefix + '_' + output_name

        try:
            convert_dir = os.path.join(out_dir, output_name, 'convert')
            os.makedirs(convert_dir, exist_ok=True)
            output_file = os.path.join(convert_dir, output_name + ".nii.gz")

            if use_dcm2niix:
                import tempfile
                import shutil

                temp = tempfile.TemporaryDirectory()
                cmd = 'dcm2niix -w 1 -z y -o {} -f {} {}'.format(temp.name, output_name, folder)
                utils.execute(cmd)
                shutil.move(os.path.join(temp.name, output_name + ".nii.gz"), output_file)
            else:
                dicom2nifti.dicom_series_to_nifti(folder, output_file, reorient_nifti=True)

            logger.info('Saved {}'.format(output_file))
            count += 1
        except Exception as ex:
            logger.warning('Processing {} encountered exception {}'.format(folder, ex))

    return utils.status(count, num_folders)


def main(argv=None):
    import sys

    argv = argv or sys.argv[1:]
    parser = utils.build_convert_arg_parser()
    args = parser.parse_args(argv)
    code, _ = convert(args.input, args.output, args.prefix, args.use_dcm2niix)
    sys.exit(code)
