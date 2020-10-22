import dicom2nifti
import os
import sys

from glob import glob

from . import utils

logger = utils.init_logger('tbi.convert')


def convert(pattern, output, prefix='', use_dcm2niix=False):
    utils.init_dicom2nifti_settings()

    folders = glob(pattern)
    logger.debug('Processing folders {}'.format(folders))
    os.makedirs(output, exist_ok=True)

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

        output_file = os.path.join(output, output_name+".nii.gz")
        logger.debug('Saving to {}'.format(output_file))

        try:
            if use_dcm2niix:
               cmd = 'dcm2niix -w 1 -z y -o {} -f {} {}'.format(output, output_name, folder)
               utils.execute(cmd)
            else:
               dicom2nifti.dicom_series_to_nifti(folder, output_file, reorient_nifti=True)

            logger.info('Saved {}'.format(output_file))
        except Exception as ex:
            logger.warning('Processing {} encountered exception {}'.format(folder, ex))

    logger.info('Done')


def main():
    parser = utils.build_convert_arg_parser()
    args = parser.parse_args(argv)
    logger.info('Using args:{}'.format(args))

    convert(args.input, args.output, args.prefix, args.use_dcm2niix)


if __name__ == '__main__':
    main(sys.argv[1:])
