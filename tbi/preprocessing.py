import os
import sys
import tempfile

from glob import glob

from . import utils 

logger = utils.init_logger('tbi.preprocessing')


def preprocessing(pattern, output, mni_file):
    file_names = glob(pattern)
    file_names.sort()
    logger.debug('Processing files {}'.format(file_names))
    os.makedirs(output, exist_ok=True)

    for file in file_names:
        logger.info('Processing file {}'.format(file))

        temp = tempfile.TemporaryDirectory()
        logger.debug('Using temporary directory {}'.format(temp))

        out1file = os.path.join(temp.name, 'out1.nii.gz')
        utils.execute('fslswapdim {} x -y z {}'.format(file, out1file))

        out2file = os.path.join(temp.name, 'out2.nii.gz')
        utils.execute('3dresample -dxyz 1.0 1.0 1.0 -orient RPI -prefix {} -inset {}'.format(out2file,
                                                                                             out1file))

        out3file = os.path.join(temp.name, 'out3.nii.gz')
        utils.execute('robustfov -i {} -r {}'.format(out2file, out3file))
        utils.execute('N4BiasFieldCorrection -d 3 -i {} -o {}'.format(out3file, out3file))

        file_name = os.path.basename(file)
        logger.debug('Processing file_name {}'.format(file_name))
        idx = file_name.index('.')
        output = os.path.join(output, file_name[0:idx])
        logger.debug('Saving to {}'.format(output))
        fmt = '{} -d 3 -n 3 -f {} -m {} -o {}_normalized -t a'
        cmd = 'antsRegistrationSyN.sh'
        utils.execute(fmt.format(cmd, mni_file, out3file, output))
        logger.info('Saved {0}'.format(output))

    logger.info('Done')


def main(argv= sys.argv[1:]):
    parser = utils.build_pre_processing_arg_parser()
    args = parser.parse_args(argv)
    logger.info('Using args:{}'.format(args))
    preprocessing(args.input, args.output, args.mni_file)


if __name__ == '__main__':
    main(sys.argv[1:])
