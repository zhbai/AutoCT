import os
from glob import glob

import dicom2nifti

from . import utils


def main():
    utils.init_dicom2nifti_settings()
    logger = utils.init_logger('tbi.convert', True)
    parser = utils.build_convert_arg_parser()
    args = parser.parse_args()

    logger.info('Using args:{0}'.format(args))

    folders = glob(args.input)

    for folder in folders:
        logger.debug('Folder: {0}'.format(folder))
        output_file = os.path.join(args.output, folder.split('/')[-2]+".nii")
        logger.info('Saving to {0}'.format(output_file))

        try:
            dicom2nifti.dicom_series_to_nifti(folder, output_file, reorient_nifti=True)
        except Exception as e:
            logger.warning('exception %s' % e)


if __name__ == '__main__':
    main()
