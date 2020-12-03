def plot_image(img, n_cuts=7):
    from nilearn.plotting.find_cuts import find_cut_slices
    import nilearn.plotting as plotting
    
    axes = ('x', 'y', 'z')
    all_cuts = [find_cut_slices(img, n_cuts=n_cuts, direction=axis) for axis in axes]
    cut_coords = [cuts[int(n_cuts/2) + 1] for cuts in all_cuts]
    plotting.plot_img(img, display_mode='ortho', cut_coords=tuple(cut_coords))
    plotting.show()
        

def plot_images(pattern):
    from glob import glob
    import nibabel as nib
    
    for nii_file in glob(pattern):
        img = nib.load(nii_file)
        shape = img.shape
        
        if len(shape) == 3:
            print('Plotting {}:shape={}'.format(nii_file, shape))
            plot_image(img)
            
        if len(shape) == 5 and shape[3] == 1 and shape[4] == 3:
            data = img.get_fdata()
            
            for v in range(3):
                print('Plotting {}:volume={}:shape={}'.format(nii_file, v+1, shape))
                img = img.__class__(data[:, :, :, :, v:v+1].squeeze(), affine=img.affine)
                plot_image(img)
        

def plot_csv_files(pattern):
    from glob import glob
    import pandas as pd
    from IPython.display import display
    
    for csv_file in glob(pattern):
        print('Plotting csv file {}'.format(csv_file))
        df = pd.read_csv(csv_file)
        display(df.iloc[0:115, 0:5])
