import os

from . import utils


def main():
    logger = utils.init_logger('tbi.template_command_syn_average', True)
    parser = utils.build_template_command_syn_average_arg_parser()
    args = parser.parse_args()
    logger.debug('Arguments: {0}'.format(args))
    cmd = 'antsMultivariateTemplateConstruction.sh'
    #template_args = '-d 3 -i 4 -g 0.2 -j 40 -c 2 -k 1 -w 1 -m 100x70x50x10 -n 1 -r 1 -s CC -t GR -b 1' 

    template_args = '-c 2 -i {0} -j {1} -m {2} {3}'.format(args.iteration_limit, args.cpu_cores, args.max_iterations, args.extra_args)
    template_args = template_args + ' -o {0}/T_ {1}/*.nii.gz'.format(args.output, args.input)
    logger.info('Calling {0} {1}'.format(cmd, template_args))
    os.system('{0} {1}'.format(cmd, template_args))


if __name__ == '__main__':
    main()
