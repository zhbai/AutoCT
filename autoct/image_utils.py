import numpy as np
import nibabel  as nib


def fix_pixdim(pixdim, ndim):
    dims = np.arange(1, 1 + ndim)
    temp = pixdim[dims]
    temp[temp == 0] = 1
    pixdim[dims] = temp


def drop_img_dim(img, only_last=True):
    header = img.header
    dim_ = header['dim'].copy()
    pdim = header['pixdim'].copy()
    fix_pixdim(pdim, dim_[0])
    imgdim = img.shape
    ndim = img.ndim + 1
    dim_[1:ndim] = imgdim
    if ndim <= len(dim_): dim_[ndim:len(dim_)] = 1
    no_data = dim_ <= 1
    no_data = np.logical_or(no_data, pdim == 0)
    no_data[0] = False

    if only_last:
        maxdim = np.amax(np.where(no_data == False))
        no_data[:maxdim + 1] = False

    ndim = np.sum(no_data == False) - 1

    if ndim < 3:
       raise Exception("cannot drop below 3 dimenssions")

    dim_[0] = ndim
    pdim = pdim[no_data == False]
    pdim = np.concatenate([pdim, np.ones(8 - len(pdim))])
    dim_ = dim_[no_data == False]
    dim_ = np.concatenate([dim_, np.ones(8 - len(dim_))])

    if len(imgdim) > ndim:
       header = header.copy()

    header['pixdim'] = pdim
    header['dim'] = dim_

    if len(imgdim) <= ndim:
         return img

    data = img.get_fdata()

    if only_last:
         cs = np.cumsum(np.flip(no_data[1 + np.arange(len(imgdim))]))
         dropcols = cs == np.arange(len(imgdim)) + 1
         dropcols = np.flip(dropcols)
         dropcols = np.where(dropcols)
         data = np.squeeze(data, axis = tuple(dropcols[0]))
    else:
         data = np.squeeze(data)

    checkdim = header['dim']
    checkdim[checkdim < 1] = 1
    header['dim'] = checkdim 
    return img.__class__(data, affine=img.affine, header=header)

def calibrate_img(img):
    data = img.get_fdata()
    cmin, cmax = data.min(), data.max()
    cmin = np.float32(cmin)
    cmax = np.float32(cmax)
    img.header.set_data_dtype(np.float32)
    img.header['cal_max'] = cmax
    img.header['cal_min'] = cmin
    img.header['glmax'] = cmax
    img.header['glmin'] = cmin


def rescale_img(img, amin=-1024, amax=3071):
    data = img.get_fdata()
    tmin, tmax = data.min(), data.max()

    if tmin < amin:
        data[data < amin] = amin

    if tmax > amax:
        data[data > amax] = amax
