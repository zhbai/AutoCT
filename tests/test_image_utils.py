import numpy as np
import nibabel as nib

from autoct.image_utils import drop_img_dim, rescale_img, calibrate_img

def test_drop_img():
    data = np.arange(5*7*23).reshape(7, 23, 1, 5, 1, 1)
    img = nib.Nifti1Image(data, affine=np.eye(4))
    arr = np.array([-1., 1., 1., 1., 0., 0., 0., 0.], dtype=np.float32)
    expected = np.array([-1., 1., 1., 1., 1., 1., 1., 1.], dtype=np.float32)
    img.header['pixdim'] = arr
    img = drop_img_dim(img)
    assert (7, 23, 1, 5) == img.shape
    assert 4 == img.header['dim'][0]
    assert (img.header['pixdim'] == expected).all()

    img.header['pixdim'] = arr
    img = nib.Nifti2Image(img.get_fdata(), header=img.header, affine=np.eye(4))
    img = drop_img_dim(img, False)
    assert (7, 23, 5) == img.shape
    assert 3 == img.header['dim'][0] 
    assert (img.header['pixdim'] == expected).all()

    img.header['pixdim'] = arr
    img = drop_img_dim(img, False)
    assert (7, 23, 5) == img.shape
    assert 3 == img.header['dim'][0] 
    assert (img.header['pixdim'] == expected).all()


def test_drop_img_with_bad_dimensions():
    try:
        data = np.arange(5*7*23).reshape(5*7, 1, 1, 23)
        img = nib.Nifti1Image(data, affine=np.eye(4))
        drop_img_dim(img, False)
    except Exception:
        pass

    try:
        data = np.arange(5*7*23).reshape(5*7, 23, 1, 1)
        img = nib.Nifti1Image(data, affine=np.eye(4))
        drop_img_dim(img, False)
    except Exception:
        pass


def test_calibrate():
    data = np.random.rand(5, 7, 11)
    expected_max = np.float32(data.max())
    expected_min = np.float32(data.min())
    img = nib.Nifti1Image(data, affine=np.eye(4))
    calibrate_img(img)
    assert img.header['cal_max'] == expected_max
    assert img.header['cal_min'] == expected_min
    assert img.header['glmax'] == np.int32(expected_max)
    assert img.header['glmin'] == np.int32(expected_min)
    assert img.header.get_data_dtype() == np.float32


def test_rescale():
    data = np.random.rand(5, 7, 11)
    expected_max = data.max()
    expected_min = data.min()
    data[0] = data.max() + 1
    data[4] = data.min() - 1
    img = nib.Nifti1Image(data, affine=np.eye(4))
    img.header.set_data_dtype(np.float64)
    rescale_img(img, expected_min, expected_max)
    data = img.get_fdata()
    assert (expected_min == data[4]).all()
    assert expected_min == data.min()
    assert (expected_max == data[0]).all()
