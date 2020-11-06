from autoct import utils


def test_replace():
    default_args = '-j 1 -m 2 -y true'
    override_args = '-y false -j 2'
    result = utils.replace(override_args, default_args)
    assert '-j 2 -m 2 -y false' == result


def test_execute():
    utils.execute('ls')


def test_bad_execute():
    try:
        utils.execute('bad_test_ommand')
        assert False
    except Exception:
        pass
