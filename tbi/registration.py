import os
from glob import glob

from . import utils

logger = utils.init_logger('tbi.registration')

def registration(pattern, output, template):
    logger.info('Arguments: {0} {1} {2}'.format(pattern, output, template))

    os.makedirs(output, exist_ok=True)

    for file in glob(pattern):
        logger.info('Processing {0}'.format(file))

        output_name = os.path.basename(file)
        idx = output_name.rindex('_brain.nii')
        output_name = output_name[:idx]
        logger.debug('Output name: {0}'.format(output_name))

        # 3 stages: rigid + affine + deformable syn (default = 's')
        outputSyn = os.path.join(output, 'SyN')
        os.makedirs(outputSyn, exist_ok=True)
        outputSyn = os.path.join(outputSyn, output_name + '_preprocessed_SyN')
        logger.info('Registering {0}'.format(file))
        utils.execute(
            'antsRegistrationSyNQuick.sh -d 3 -n 4 -f {0} -m {1} -o {2}'.format(
                template, file, outputSyn))

        # 2 stages: rigid + affine
        outputAffine = os.path.join(output, 'Affine')
        os.makedirs(outputAffine, exist_ok=True)
        outputAffine = os.path.join(outputAffine, output_name + '_preprocessed_affine')
        utils.execute(
            'antsRegistrationSyNQuick.sh -d 3 -n 4 -f {0} -m {1} -o {2} -t a'.format(
                template, file, outputAffine))

        # 1 stage: deformable syn only
        outputAffine2Syn = os.path.join(output, 'Affine2SyN')
        os.makedirs(outputAffine2Syn, exist_ok=True)
        outputAffine2Syn = os.path.join(outputAffine2Syn, output_name + '_preprocessed_affine2Syn')
        utils.execute(
            'antsRegistrationSyNQuick.sh -d 3 -n 4 -f {0} -m {1} -o {2} -t so'.format(
                template, outputAffine + 'Warped.nii.gz',  outputAffine2Syn))

    logger.info('Done')

import sys

def main(argv=sys.argv[1:]):
    parser = utils.build_registration_arg_parser()
    args = parser.parse_args(argv)
    logger.info('Arguments: {0}'.format(args))
    registration(args.input, args.output, args.template_file)


if __name__ == '__main__':
    main(sys.argv[1:])
