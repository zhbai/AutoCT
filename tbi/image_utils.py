import numpy as np


def calibrate_image(img):
    data = img.get_fdata()
    cmin, cmax = np.amin(data), np.amax(data)
    cmin = np.float32(cmin)
    cmax = np.float32(cmax)
    img.header.set_data_dtype(np.float32)
    img.header['cal_max'] = cmax
    img.header['cal_min'] = cmin
    img.header['glmax'] = cmax
    img.header['glmin'] = cmin
    arr = np.array([-1., 1., 1., 1., 1., 1., 1., 1.], dtype=np.float32)
    img.header['pixdim'] = arr


def rescale(img, aamin=-1024, aamax=3071):
    data = img.get_fdata()
    tmin, tmax = np.amin(data), np.amax(data)

    if tmin < aamin or tmax > aamax:
        data[data < aamin] = aamin
        data[data > aamax] = aamax

    img.header.set_data_dtype(np.float32)
    img.header['descrip'] = b'written by dcm2nii - '
