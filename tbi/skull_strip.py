import os

from . import utils

if __name__ == '__main__':
    logger = utils.init_logger('tbi.skull_strip', True)
    parser = utils.build_skull_strip_arg_parser()
    args = parser.parse_args()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    script = os.path.join(dir_path, 'skull_strip.R') 
    logger.info(dir_path)
    logger.info(script)
    os.system('Rscript {0} {1} {2}'.format(script, args.input, args.output))
