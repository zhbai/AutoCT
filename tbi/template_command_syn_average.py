import os

from . import utils


def main():
    logger = utils.init_logger('tbi.template_command_syn_average', True)
    parser = utils.build_template_command_syn_average_arg_parser()
    args = parser.parse_args()
    logger.debug('Arguments: {0}'.format(args))
    #script = utils.locate_script(__file__, 'template_command_syn_average.sh')
    #logger.debug('Using bash script at {0}'.format(script))
    #os.system('{0} {1} {2}'.format(script, args.input, args.output))
    cmd = 'antsMultivariateTemplateConstruction.sh'
    template_args = '-d 3 -i 4 -g 0.2 -j 40 -c 2 -k 1 -w 1 -m 3500000 -n 1 -r 1 -s CC -t GR -b 1' 
    template_args = template_args + ' -o {0}T_ {1}/*.nii.gz'.format(args.output, args.input)
    os.system('{0} {1}'.format(cmd, template_args))


if __name__ == '__main__':
    main()
