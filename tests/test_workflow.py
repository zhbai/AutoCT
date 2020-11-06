from os.path import join

import tbi


def test_workflow():
    import tempfile

    temp_dir = tempfile.TemporaryDirectory()
    output = temp_dir.name
    mni_file = 'notebooks/illustration_data/MNI152_T1_1mm_brain.nii.gz'
    atlas_file = 'notebooks/illustration_data/New_atlas_cort_asym_sub.nii.gz'
    template_file = 'notebooks/illustration_data/T_template0.nii.gz'

    ret, _ = tbi.convert(pattern='notebooks/illustration_data/dcmfiles/*',
                         out_dir=join(output, 'convert'),
                         use_dcm2niix=True)
    assert ret == 0, 'convert failed'

    ret, _ = tbi.preprocessing(pattern=join(output, 'convert', '*.nii.gz'),
                               out_dir=join(output, 'preprocessing'),
                               mni_file=mni_file)
    assert ret == 0, 'preprocessing failed'

    ret, _ = tbi.skull_strip(pattern=join(output, 'preprocessing', '*.nii.gz'),
                             out_dir=join(output, 'brains'))
    assert ret == 0, 'skull_strip failed'

    ret, _ = tbi.registration(pattern=join(output, 'brains', '*.nii.gz'),
                              out_dir=join(output, 'registration'),
                              template=template_file,
                              transforms=tbi.supported_registration_transforms())
    assert ret == 0, 'registration failed'

    ret, _ = tbi.segmentation(pattern=join(output, 'registration', '*/*.nii.gz'),
                              out_dir=join(output, 'segmentation'),
                              atlas=atlas_file,
                              types=tbi.supported_segmentation_types())

    assert ret == 0, 'segmentation failed'

    ret, _ = tbi.label_geometry_measures(pattern=join(output, 'segmentation', '*/*.nii.gz'),
                                         out_dir=join(output, 'label_geometry_measures'))
    assert ret == 0, 'label_geometry_measures failed'

    ret, _ = tbi.image_intensity_stat(pattern=join(output, 'registration', '*/*.nii.gz'),
                                      out_dir=join(output, 'image_intensity_stat'),
                                      atlas=atlas_file)
    assert ret == 0, 'image_intensity_stat failed'
