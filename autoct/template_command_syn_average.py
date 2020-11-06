from . import utils
from glob import glob


def syn_average(pattern, output, extra_args):
    logger = utils.init_logger('autoct.template_command_syn_average')
    logger.info('Arguments: {}:{}:{}'.format(pattern, output, extra_args))
    files = glob(pattern or '')

    if len(files) < 2:
        raise Exception('Must  provide at least two nii files: Found {}'.format(files))

    logger.debug('Using {} files'.format(files))

    cmd = 'antsMultivariateTemplateConstruction.sh'
    template_args = utils.replace(extra_args, utils.default_template_extra_args())
    logger.info('Using {}'.format(template_args))
    template_args = template_args + ' -o {}/T_ {}'.format(output, pattern)
    utils.execute('{} {}'.format(cmd, template_args))
    logger.info('Done')


def main(argv=None):
    import sys

    parser = utils.build_template_command_syn_average_arg_parser()
    argv = argv or sys.argv[1:]
    args = parser.parse_args(argv)
    syn_average(args.input, args.output, args.extra_args)
