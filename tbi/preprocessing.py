import os
import tempfile

from . import utils 


def preprocessing(argv):
    logger = utils.init_logger('tbi.preprocessing', True)
    parser = utils.build_pre_processing_arg_parser()
    args = parser.parse_args(argv)
    logger.info('Using args:{0}'.format(args))
    
    file_names = os.listdir(args.input)
    file_names.sort()
    logger.debug('Processing files {0}'.format(file_names))
    os.makedirs(args.output, exist_ok=True)

    for file_name in file_names:
        file = os.path.join(args.input, file_name)
        logger.info('Processing file {0}'.format(file))

        temp = tempfile.TemporaryDirectory()
        logger.debug('Using temporary directory {0}'.format(temp))

        out1file = os.path.join(temp.name, 'out1.nii.gz')
        os.system('fslswapdim {0} x -y z {1}'.format(file, out1file))

        out2file = os.path.join(temp.name, 'out2.nii.gz')
        os.system('3dresample -dxyz 1.0 1.0 1.0 -orient RPI -prefix {0} -inset {1}'.format(out2file,
                                                                                           out1file))

        out3file = os.path.join(temp.name, 'out3.nii.gz')
        os.system('robustfov -i {0} -r {1}'.format(out2file, out3file))
        os.system('N4BiasFieldCorrection -d 3 -i {0} -o {1}'.format(out3file, out3file))

        idx = file_name.rindex('.')
        output = os.path.join(args.output, file_name[0:idx])
        logger.debug('Saving to {0}'.format(output))

        os.system(
            'antsRegistrationSyN.sh -d 3 -n 3 -f {0} -m {1} -o {2}_normalized -t a'.format(args.mni_file,
                                                                                            out3file,
                                                                                            output))
        logger.info('Saved {0}'.format(output))

    logger.info('Exiting!')

def main():
    import sys

    preprocessing(sys.argv[1:])


if __name__ == '__main__':
    main()
