import os
from glob import glob

import dicom2nifti

from . import utils


def convert(argv):
    utils.init_dicom2nifti_settings()
    logger = utils.init_logger('tbi.convert', True)
    parser = utils.build_convert_arg_parser()
    args = parser.parse_args(argv)
    logger.info('Using args:{0}'.format(args))

    folders = glob(args.input)
    logger.debug('Processing folders {0}'.format(folders))
    os.makedirs(args.output, exist_ok=True)

    for folder in folders:
        logger.info('Processing folder {0}'.format(folder))

        if folder.endswith('/'): 
           output_name = os.path.basename(os.path.dirname(folder)) 
        else:
           output_name = os.path.basename(folder) 

        output_name = output_name.replace(' ', '_')
        output_name = output_name.replace('.', '_')

        if args.prefix:
           output_name = args.prefix + '_' + output_name

        output_file = os.path.join(args.output, output_name+".nii.gz")
        logger.debug('Saving to {0}'.format(output_file))

        try:
            if args.use_dcm2niix:
               cmd = 'dcm2niix -w 1 -z y -o {0} -f {1} {2}'.format(args.output, output_name, folder)
               utils.execute(cmd)
            else:
               dicom2nifti.dicom_series_to_nifti(folder, output_file, reorient_nifti=True)

            logger.info('Saved {0}'.format(output_file))
        except Exception as ex:
            logger.warning('Processing {0} encountered exception {1}'.format(folder, ex))

    logger.info('Done')


def main():
    import sys

    convert(sys.argv[1:])


if __name__ == '__main__':
    main()
