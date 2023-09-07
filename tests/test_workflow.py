from os.path import join

import autoct


def test_workflow():
    import tempfile

    temp_dir = tempfile.TemporaryDirectory()
    output = temp_dir.name
    mni_file = 'notebooks/illustration_data/MNI152_T1_1mm_brain.nii.gz'
    atlas_file = 'notebooks/illustration_data/New_atlas_cort_asym_sub.nii.gz'
    template_file = 'notebooks/illustration_data/T_template0.nii.gz'

    ret, _ = autoct.convert(pattern='notebooks/illustration_data/dcmfiles/*',
                            out_dir=output,
                            use_dcm2niix=True)
    assert ret == 0, 'convert failed'

    ret, _ = autoct.preprocessing(pattern=join(output, '*', 'convert', '*.nii.gz'),
                                  out_dir=output,
                                  mni_file=mni_file)
    assert ret == 0, 'preprocessing failed'

    ret, _ = autoct.bone_strip(pattern=join(output, '*', 'preprocessing', '*.nii.gz'),
                               out_dir=output)
    assert ret == 0, 'bone_strip failed'

    ret, _ = autoct.registration(pattern=join(output, '*', 'bone_strip', '*.nii.gz'),
                                 out_dir=output,
                                 template=template_file,
                                 transforms=autoct.supported_registration_transforms())
    assert ret == 0, 'registration failed'

    ret, _ = autoct.segmentation(pattern=join(output, '*', 'registration', '*/*.nii.gz'),
                                 out_dir=output,
                                 atlas=atlas_file,
                                 types=autoct.supported_segmentation_types())

    assert ret == 0, 'segmentation failed'

    ret, _ = autoct.label_geometry_measures(pattern=join(output, '*', 'segmentation', '*/*.nii.gz'),
                                            out_dir=output)
    assert ret == 0, 'label_geometry_measures failed'

    ret, _ = autoct.warp_intensity_stats(pattern=join(output, '*', 'registration', '*/*.nii.gz'),
                                         out_dir=output,
                                         atlas=atlas_file)
    assert ret == 0, 'warp_intensity_stats failed'
