import os
import time
from glob import glob

from . import utils

logger = utils.init_logger('tbi.segmentation')

def segmentation(pattern, output, atlas):
    logger.info('Arguments: {0} {1} {2}'.format(pattern, output, atlas))

    os.makedirs(output, exist_ok=True)

    for file_name in glob(pattern):
        if file_name.endswith('_preprocessed_SyN1InverseWarp.nii.gz'):
            # SEGMENTATION OF THE ORIGINAL CT SCAN OF PATIENT
            logger.info('Processing {0}'.format(file_name))
            output_name = os.path.basename(file_name)
            idx = output_name.rindex('_preprocessed_SyN1InverseWarp.nii.gz')
            output_name = output_name[:idx]

            dir_name = os.path.dirname(file_name)
            mat_file = os.path.join(dir_name, output_name + '_preprocessed_SyN0GenericAffine.mat')

            if not os.path.isfile(mat_file):
                logger.warn('Did not find matching mat file for {0}'.format(file_name))
                continue

            outputSeg = os.path.join(output, 'PHYSCi')
            os.makedirs(outputSeg, exist_ok=True)
            outputSeg = os.path.join(outputSeg, output_name + '_segmentation_cortical_phy.nii.gz')
            transforms = '[' + mat_file + ',1] ' + file_name 
            fmt = '{} -f 0 -d 3 -n GenericLabel[Linear] -i {} -o {} -r {} -t {}'
            cmd = 'antsApplyTransforms'
            start = time.time()
            utils.execute(fmt.format(cmd, atlas, outputSeg, file_name, transforms))
            end = time.time()
            logger.info("Physical: {0}".format(end - start))

    for file_name in glob(pattern):
         if file_name.endswith('_preprocessed_affine2Syn1InverseWarp.nii.gz'):
            # SEGMENTATION OF THE AFFINE TRANSFORMED DATA
            logger.info('Processing {0}'.format(file_name))
            output_name = os.path.basename(file_name)
            idx = output_name.rindex('_preprocessed_affine2Syn1InverseWarp.nii.gz')
            output_name = output_name[:idx]

            dir_name = os.path.dirname(file_name)
            mat_file = os.path.join(dir_name, output_name + '_preprocessed_affine2Syn0GenericAffine.mat')

            if not os.path.isfile(mat_file):
                logger.warn('Did not find matching mat file for {0}'.format(file_name))
                continue

            dir_name = os.path.dirname(dir_name)
            outputAffine = os.path.join(dir_name, 'Affine')
            affine_file = os.path.join(outputAffine, output_name + '_preprocessed_affineWarped.nii.gz')

            if not os.path.isfile(affine_file):
                logger.warn('Did not find matching warped affine file for {0}'.format(file_name))
                continue

            outputSeg = os.path.join(output, 'AFFINE')
            os.makedirs(outputSeg, exist_ok=True)
            outputSeg = os.path.join(outputSeg, output_name + '_segmentation_cortical_affine.nii.gz')
            transforms = '[' + mat_file + ',1] ' + file_name 
            fmt = '{} -f 0 -d 3 -n GenericLabel[Linear] -i {} -o {} -r {} -t {}'
            cmd = 'antsApplyTransforms'
            start = time.time()
            utils.execute(fmt.format(cmd, atlas, outputSeg, affine_file, transforms)) 
            end = time.time()
            logger.info("Affine: {0}".format(end - start))

    logger.info('Done')


import sys

def main(argv=sys.argv[1:]):
    parser = utils.build_segmentation_arg_parser()
    args = parser.parse_args(argv)
    logger.info('Arguments: {0}'.format(args))
    segmentation(args.input, args.output, args.atlas_file)


if __name__ == '__main__':
    main(sys.argv[1:])
