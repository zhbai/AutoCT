import os
import time
from glob import glob

from . import utils


def segmentation(argv):
    logger = utils.init_logger('tbi.segmentation', True)
    parser = utils.build_segmentation_arg_parser()
    args = parser.parse_args(argv)
    logger.info('Arguments: {0}'.format(args))

    template = args.template_file
    atlas = args.atlas_file

    os.makedirs(args.output, exist_ok=True)

    for file in glob(args.input):
        logger.info('Processing {0}'.format(file))

        output_name = os.path.basename(file)
        idx = output_name.rindex('_brain.nii.gz')
        output_name = output_name[:idx]
        logger.debug('Output name: {0}'.format(output_name))

        # 3 stages: rigid + affine + deformable syn (default = 's')
        outputSyn = os.path.join(args.output, 'REGIS', 'SyN')
        os.makedirs(outputSyn, exist_ok=True)
        outputSyn = os.path.join(outputSyn, output_name + '_preprocessed_SyN')
        logger.info('Registering {0}'.format(file))
        utils.execute(
            'antsRegistrationSyNQuick.sh -d 3 -n 4 -f {0} -m {1} -o {2}'.format(
                template, file, outputSyn))

        # 2 stages: rigid + affine
        outputAffine = os.path.join(args.output, 'REGIS', 'Affine')
        os.makedirs(outputAffine, exist_ok=True)
        outputAffine = os.path.join(outputAffine, output_name + '_preprocessed_affine')
        utils.execute(
            'antsRegistrationSyNQuick.sh -d 3 -n 4 -f {0} -m {1} -o {2} -t a'.format(
                template, file, outputAffine))

        # 1 stage: deformable syn only
        outputAffine2Syn = os.path.join(args.output, 'REGIS', 'Affine2SyN')
        os.makedirs(outputAffine2Syn, exist_ok=True)
        outputAffine2Syn = os.path.join(outputAffine2Syn, output_name + '_preprocessed_affine2Syn')
        utils.execute(
            'antsRegistrationSyNQuick.sh -d 3 -n 4 -f {0} -m {1} -o {2} -t so'.format(
                template, outputAffine + 'Warped.nii.gz',  outputAffine2Syn))

        # SEGMENTATION OF THE ORIGINAL CT SCAN OF PATIENT
        start = time.time()
        outputSeg = os.path.join(args.output, 'SEG', 'PHYSCi')
        os.makedirs(outputSeg, exist_ok=True)
        outputSeg = os.path.join(outputSeg, output_name + '_segmentation_cortical_phy.nii.gz')
        transforms = '[' + outputSyn + '0GenericAffine.mat,1] ' + outputSyn + '1InverseWarp.nii.gz'
        utils.execute(
            'antsApplyTransforms -f 0 -d 3 -n GenericLabel[Linear] -i {0} -o {1} -r {2} -t {3}'.format(
                atlas, outputSeg, file, transforms))
        end = time.time()
        logger.info("Physical: {0}".format(end - start))

        # SEGMENTATION OF THE AFFINE TRANSFORMED DATA
        start = time.time()
        outputSeg = os.path.join(args.output, 'SEG', 'AFFINE')
        os.makedirs(outputSeg, exist_ok=True)
        outputSeg = os.path.join(outputSeg, output_name + '_segmentation_cortical_affine.nii.gz')
        transforms = '[' + outputAffine2Syn + '0GenericAffine.mat,1] ' + outputAffine2Syn + '1InverseWarp.nii.gz'
        utils.execute(
            'antsApplyTransforms -f 0 -d 3 -n GenericLabel[Linear] -i {0} -o  {1} -r {2}Warped.nii.gz -t {3}'.format(
                atlas, outputSeg, outputAffine, transforms))
        end = time.time()
        logger.info("Affine: {0}".format(end - start))

    logger.info('Done')


def main():
    import sys

    segmentation(sys.argv[1:])


if __name__ == '__main__':
    main()
