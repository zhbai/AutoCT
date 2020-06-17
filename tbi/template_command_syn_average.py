import os

from . import utils


def main():
    logger = utils.init_logger('tbi.skull_strip', True)
    parser = utils.build_template_command_syn_average_arg_parser()
    args = parser.parse_args()
    logger.debug('Arguments: {0}'.format(args))
    script = utils.locate_script(__file__, 'template_command_syn_average.sh')
    logger.debug('Using bash script at {0}'.format(script))
    os.system('{0} {1} {2}'.format(script, args.input, args.output))


if __name__ == '__main__':
    main()
