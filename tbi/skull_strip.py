import os

from . import utils


def main():
    logger = utils.init_logger('tbi.skull_strip', True)
    parser = utils.build_skull_strip_arg_parser()
    args = parser.parse_args()
    logger.debug('Arguments: {0}'.format(args))
    script = utils.locate_script(__file__, 'skull_strip.R')
    logger.debug('Using R script at {0}'.format(script))
    os.system('Rscript {0} {1} {2}'.format(script, args.input, args.output))


if __name__ == '__main__':
    main()
