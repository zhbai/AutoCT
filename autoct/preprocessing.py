import os
import tempfile

from glob import glob

from . import utils 

logger = utils.init_logger('autoct.preprocessing')


def __preprocessing(file, out_dir, mni_file):
    logger.info('Processing {}'.format(file))
    temp = tempfile.TemporaryDirectory()
    out1file = os.path.join(temp.name, 'swapped.nii.gz')
    utils.execute('fslswapdim {} x -y z {}'.format(file, out1file))
    from . import resample
    import shutil

    if shutil.which('3dresample'):
        logger.info('Using afni binary 3dreample ...')
        out2file = os.path.join(temp.name, 'resampled_and_reoriented.nii.gz')
        utils.execute('3dresample -dxyz 1.0 1.0 1.0 -orient RPI -inset {} -prefix {}'.format(out1file, out2file))
    else:
        cwd = os.getcwd()
        os.chdir(temp.name)
        logger.info('Using python based resampling ...')
        temp_file = os.path.join(temp.name, 'resampled.nii.gz')
        resample.do_resample(out1file, temp_file)
        out2file = os.path.join(temp.name, 'reoriented.nii.gz')
        resample.do_reorient(temp_file, out2file)
        os.chdir(cwd)

    out3file = os.path.join(temp.name, 'reduced.nii.gz')
    utils.execute('robustfov -i {} -r {}'.format(out2file, out3file))

    out4file = os.path.join(temp.name, 'corrected.nii.gz')
    utils.execute('N4BiasFieldCorrection -d 3 -i {} -o {}'.format(out3file, out4file))

    prefix = utils.prefix(file, '.nii')
    preprocessing_dir = os.path.join(out_dir, prefix, 'preprocessing') 
    os.makedirs(preprocessing_dir, exist_ok=True)
    out_file = os.path.join(preprocessing_dir, prefix)
    fmt = '{} -d 3 -n 3 -f {} -m {} -o {}_normalized -t a'
    cmd = 'antsRegistrationSyN.sh'
    utils.execute(fmt.format(cmd, mni_file, out4file, out_file))
    logger.info('Saved to {}'.format(out_file))


def preprocessing(pattern, out_dir, mni_file):
    """Process image orientation, voxel size/resolution, bias correction and pre-alignment.

    Parameters
    ----------
        pattern : str
            Glob path expression to locate nii images
        out_dir  : str
            Output Directory
        mni_file : str
            Path to mni file
    """

    logger.info('Arguments: {}:{}:{}'.format(pattern, out_dir,  mni_file))
    if not os.path.isfile(mni_file):
        err_msg = 'Did not find mni file {}'.format(mni_file)
        logger.error(err_msg)
        return -1, err_msg

    files = glob(pattern or '')
    num_files = len(files)

    if not num_files:
        err_msg = 'Did not find any input file matching {}'.format(pattern)
        logger.error(err_msg)
        return -1, err_msg

    try:
        os.makedirs(out_dir, exist_ok=True)
    except Exception as ex:
        err_msg = 'Error creating directory {}'.format(ex)
        logger.error(err_msg)
        return -1, err_msg

    count = 0
    logger.info('Found {} files'.format(num_files))

    for file in files:
        try:
            __preprocessing(file, out_dir, mni_file)
            count += 1
        except Exception as ex:
            logger.warning('Processing {} encountered exception {}'.format(file, ex))
            import traceback

            traceback.print_exception(ex)

    return utils.status(count, num_files)


def main(argv=None):
    import sys

    argv = argv or sys.argv[1:]
    parser = utils.build_pre_processing_arg_parser()
    args = parser.parse_args(argv)
    logger.info('Using args:{}'.format(args))
    code, _ = preprocessing(args.input, args.output, args.mni_file)
    sys.exit(code)
