import os

from . import utils


def main():
    logger = utils.init_logger('tbi.template_command_syn_average', True)
    parser = utils.build_template_command_syn_average_arg_parser()
    args = parser.parse_args()
    logger.debug('Arguments: {0}'.format(args))
    cmd = 'antsMultivariateTemplateConstruction.sh'
    template_args = utils.replace(args.extra_args, utils.default_template_extra_args())
    template_args = template_args + ' -o {0}/T_ {1}/*.nii.gz'.format(args.output, args.input)
    logger.info('Calling {0} {1}'.format(cmd, template_args))
    os.system('{0} {1}'.format(cmd, template_args))


if __name__ == '__main__':
    main()
