from . import utils
from glob import glob


def syn_average(argv):
    logger = utils.init_logger('tbi.template_command_syn_average', True)
    parser = utils.build_template_command_syn_average_arg_parser()
    args = parser.parse_args(argv)
    logger.debug('Arguments: {0}'.format(args))
    files = glob(args.input)

    if len(files) < 2:
        raise Exception('Must  provide at least two nii files: Found {0}'.format(files))

    logger.debug('Using {0} files'.format(files))

    cmd = 'antsMultivariateTemplateConstruction.sh'
    template_args = utils.replace(args.extra_args, utils.default_template_extra_args())
    template_args = template_args + ' -o {0}/T_ {1}'.format(args.output, args.input)
    utils.execute('{0} {1}'.format(cmd, template_args))


def main():
    import sys

    syn_average(sys.argv[1:])


if __name__ == '__main__':
    main()
