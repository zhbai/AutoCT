#!/usr/bin/env python
# coding: utf-8

import ipywidgets as widgets

from IPython.display import display
from os.path import join, isfile, isdir
from functools import partial

import autoct


class ImageViewer:
    def __init__(self, img):
        self.img = img
        self.update = 0
        self.sliders = []
        self.out = None
        self.outer_output = None

    @classmethod
    def create_slider(cls, value, amin, amax, direction):
        return widgets.IntSlider(value=value,
                                 min=amin,
                                 max=amax,
                                 step=1,
                                 continuous_update=False,
                                 description=direction)

    def display_image(self, output):
        from nilearn.plotting.find_cuts import find_cut_slices

        n_cuts = 5
        axes = ('x', 'y', 'z')
        all_cuts = [find_cut_slices(self.img, n_cuts=n_cuts, direction=axis) for axis in axes]

        for i, axis in enumerate(axes):
            cuts = all_cuts[i]
            amin, amax = cuts.min(), cuts.max()
            value = int((amax + amin) / 2)
            self.sliders.append(self.create_slider(value, amin, amax, axis))

        children = [widgets.interactive(self._plot_slice, view=slider) for slider in self.sliders]
        layout = widgets.Layout(
            display='flex', flex_flow='row', align_items='stretch', width='95%')
        slider_box = widgets.Box(children=children, layout=layout)
        layout = widgets.Layout(height='200px', width='95%', border='4px solid blue', overflow_y='scroll')
        self.out = widgets.Output(layout=layout)
        box = widgets.VBox(children=[slider_box, self.out])
        self.outer_output = output
        display(box)

    def _plot_slice(self, view):
        import nilearn.plotting as plotting
        self.update += 1

        if self.update < 3:
            return

        with self.outer_output:
            with self.out:
                self.out.clear_output()
                cut_coords = tuple(slider.value for slider in self.sliders)
                plotting.plot_img(self.img, display_mode='ortho', cut_coords=cut_coords)
                plotting.show()


def display_image(img, output=None, use_viewer=True):
    import nilearn.plotting as plotting
    if use_viewer:
        viewer = ImageViewer(img)
        viewer.display_image(output)
    else:
        plotting.plot_img(img)
        plotting.show()


class Inputs:
    _outdir = '/output/illustration_output'
    _mni = 'illustration_data/MNI152_T1_1mm_brain.nii.gz'
    _atlas = 'illustration_data/New_atlas_cort_asym_sub.nii.gz'
    _template = 'illustration_data/T_template0.nii.gz'

    dcmfiles = 'illustration_data/dcmfiles/*/'
    cache = {}

    @classmethod
    def outdir(cls):
        return cls._outdir

    @classmethod
    def atlas(cls):
        return cls._atlas

    @classmethod
    def template(cls):
        return cls._template

    @classmethod
    def mni(cls):
        return cls._mni

    @classmethod
    def to_cache(cls, key, textfield):
        textfields = cls.cache.get(key)

        if textfields is None:
            textfields = [textfield]
            cls.cache[key] = textfields
        else:
            textfields.append(textfield)

    @classmethod
    def convert_input_pattern(cls):
        return cls.dcmfiles

    @classmethod
    def convert_output_dir(cls):
        return cls.outdir()

    @classmethod
    def preprocessing_input_pattern(cls, pattern='*.nii.gz'):
        return join(cls.convert_output_dir(), '*', 'convert' , pattern)

    @classmethod
    def preprocessing_output_dir(cls):
        return cls.outdir()

    @classmethod
    def bone_strip_input_pattern(cls, pattern='*.nii.gz'):
        return join(cls.preprocessing_output_dir(), '*', 'preprocessing', pattern)

    @classmethod
    def bone_strip_output_dir(cls):
        return cls.outdir()

    @classmethod
    def registration_input_pattern(cls, pattern='*.nii.gz'):
        return join(cls.bone_strip_output_dir(), '*', 'bone_strip', pattern)

    @classmethod
    def registration_output_dir(cls):
        return cls.outdir()

    @classmethod
    def segmentation_input_pattern(cls, pattern='*/*.nii.gz'):
        return join(cls.registration_output_dir(), '*', 'registration', pattern)

    @classmethod
    def segmentation_output_dir(cls):
        return cls.outdir()

    @classmethod
    def geo_input_pattern(cls, pattern='*/*.nii.gz'):
        return join(cls.segmentation_output_dir(), '*', 'segmentation', pattern)

    @classmethod
    def geo_output_dir(cls):
        return cls.outdir()

    @classmethod
    def stat_input_pattern(cls, pattern='Affine2SyN/*affine2Syn1Warp.nii.gz'):
        return join(cls.registration_output_dir(), '*', 'registration', pattern)

    @classmethod
    def stat_output_dir(cls):
        return cls.outdir()


def create_html(text, layout=widgets.Layout(height='100px', width='90%', size='10')):
    space_box = widgets.Box(layout=widgets.Layout(height='25px', width='90%'))
    return widgets.VBox([widgets.HTML(text, layout=layout), space_box])


def create_textfield(value, layout=widgets.Layout(width="60%")):
    textfield = widgets.Text(layout=layout)

    if callable(value):
        textfield.value = value()
        Inputs.to_cache(value, textfield)
    else:
        textfield.value = value

    return textfield


def create_checkbox(description):
    return widgets.Checkbox(value=True, description=description, disabled=False, indent=False)


def create_label(value, layout=widgets.Layout(width='18%')):
    return widgets.Label(value=value, layout=layout)


def create_checkbox_box(description):
    checkbox = create_checkbox(description)
    box = widgets.Box([create_label(''), checkbox])
    return box, checkbox


def create_checkboxes_box(descriptions):
    checkboxes = []
    for description in descriptions:
        checkboxes.append(create_checkbox(description))

    temp = widgets.Box([*checkboxes], layout=widgets.Layout(width="30%"))
    box = widgets.Box([create_label(''), temp])
    return box, checkboxes


def create_textfield_box(label, value):
    textfield = create_textfield(value)
    box = widgets.Box([create_label(label), textfield])
    return box, textfield


def create_space_box():
    return widgets.Box([create_label('')])


def create_button_box(*buttons):
    temp = [create_label('')]

    for button in buttons:
        temp.append(button)

    return widgets.Box(children=temp)


def create_panel(*boxes):
    buttons = boxes[-1]
    temp = list(boxes[:-1])

    for i in range(5 - len(temp)):
        temp.append(create_space_box())

    temp.append(widgets.Box(layout=widgets.Layout(height='4px')))
    temp.append(buttons)
    temp.append(widgets.Box(layout=widgets.Layout(height='3px')))
    return widgets.VBox(children=temp)


def apply_inputs(output, output_dir_textfield, template_textfield, atlas_textfield, mni_textfield, b):
    from autoct import utils
    
    logger = utils.init_logger('autoct.gui')
    output.clear_output()

    with output:
        err = False
        
        if isdir(output_dir_textfield.value):
            logger.warning('warning: directory exists ... {}'.format(output_dir_textfield.value))

        if not isfile(template_textfield.value):
            err = True
            logger.error('template file does not exist {}'.format(template_textfield.value))

        if not isfile(atlas_textfield.value):
            err = True
            logger.error('atlas file does not exist {}'.format(atlas_textfield.value))

        if not isfile(mni_textfield.value):
            err = True
            logger.error('mni file does not exist {}'.format(mni_textfield.value))

        if err:
            return

        Inputs._outdir = output_dir_textfield.value
        Inputs._template = template_textfield.value
        Inputs._atlas = atlas_textfield.value
        Inputs._mni = mni_textfield.value

        for func, lst in Inputs.cache.items():
            for textfield in lst:
                textfield.value = func()
                
        logger.info('Inputs have been applied sucessfully')


def show_images(output, pattern, output_dir_textfield, b):
    from glob import glob
    import nibabel as nib

    output.clear_output()

    with output:
        for nii_file in glob(join(output_dir_textfield.value, pattern)):
            img = nib.load(nii_file)
            shape = img.shape

            if len(shape) == 3:
                print('Plotting {}:shape={}'.format(nii_file, shape))
                display_image(img, output)

            if len(shape) == 5 and shape[3] == 1 and shape[4] == 3:
                data = img.get_fdata()

                for v in range(3):
                    print('Plotting {}:volume={}:shape={}'.format(nii_file, v + 1, shape))
                    img = img.__class__(data[:, :, :, :, v:v + 1].squeeze(), affine=img.affine)
                    display_image(img, output)


def show_csv(output, pattern, output_dir_textfield, b):
    from glob import glob
    import pandas as pd

    output.clear_output()
    with output:
        csv_files = glob(join(output_dir_textfield.value, pattern))

        for csv_file in csv_files:
            print('Displaying csv file', csv_file)
            df = pd.read_csv(csv_file)
            display(df)

def run_convert(output, pattern_textfield, use_dcm2niix_checkbox, output_dir_textfield, b):
    output.clear_output()

    with output:
        autoct.convert(pattern_textfield.value,
                       output_dir_textfield.value,
                       use_dcm2niix=use_dcm2niix_checkbox.value)

def run_preprocessing(output, mni_textfield,
                      pattern_textfield,
                      output_dir_textfield,
                      b):
    output.clear_output()
    with output:
        autoct.preprocessing(pattern_textfield.value,
                             output_dir_textfield.value,
                             mni_textfield.value)


def run_bone_strip(output, pattern_textfield, output_dir_textfield, b):
    output.clear_output()

    with output:
        autoct.bone_strip(pattern_textfield.value, output_dir_textfield.value)


def run_registration(output,
                     template_textfield,
                     checkboxes,
                     pattern_textfield,
                     output_dir_textfield,
                     b):
    output.clear_output()
    with output:
        transforms = []

        for checkbox in checkboxes:
            if checkbox.value:
                transforms.append(checkbox.description)

        autoct.registration(pattern_textfield.value,
                            output_dir_textfield.value,
                            template_textfield.value,
                            transforms)


def run_segmentation(output,
                     atlas_textfield,
                     checkboxes,
                     pattern_textfield,
                     output_dir_textfield,
                     run_button):
    output.clear_output()
    with output:
        seg_types = []

        for checkbox in checkboxes:
            if checkbox.value:
                seg_types.append(checkbox.description)

        autoct.segmentation(pattern_textfield.value,
                            output_dir_textfield.value,
                            atlas_textfield.value,
                            seg_types)


def run_label_geometry_measures(output, pattern_textfield, output_dir_textfield, b):
    output.clear_output()
    with output:
        autoct.label_geometry_measures(pattern_textfield.value,
                                       output_dir_textfield.value)


def run_intensity_stat(output, atlas_textfield,
                       pattern_textfield,
                       output_dir_textfield,
                       run_button):
    output.clear_output()
    with output:
        autoct.warp_intensity_stats(pattern_textfield.value,
                                    output_dir_textfield.value,
                                    atlas_textfield.value)


def create_input_box(output, header):
    html = create_html(header)

    box1, outdir_textfield = create_textfield_box('Top Level Ouput Directory:', Inputs.outdir())
    box2, template_textfield = create_textfield_box('Template File:', Inputs.template())
    box3, atlas_textfield = create_textfield_box('Atlas File:', Inputs.atlas())
    box4, mni_textfield = create_textfield_box('MNI File:', Inputs.mni())

    apply_button = widgets.Button(description="Apply", button_style='success')
    state = (output, outdir_textfield, template_textfield, atlas_textfield, mni_textfield)
    apply_button.on_click(partial(apply_inputs, *state))
    button_box = create_button_box(apply_button)

    return create_panel(html, box1, box2, box3, box4, button_box)


def create_convert_box(output, header):
    html = create_html(header)

    box1, pattern_textfield = create_textfield_box('Input Pattern:', Inputs.convert_input_pattern)
    box2, checkbox = create_checkbox_box('Use dcm2niix')
    box3, outdir_textfield = create_textfield_box('Output Directory:', Inputs.convert_output_dir)

    run_button = widgets.Button(description="Run", button_style='success')
    show_button = widgets.Button(description="Show", button_style='info')
    state = (output, pattern_textfield, checkbox, outdir_textfield)
    run_button.on_click(partial(run_convert, *state))
    show_button.on_click(partial(show_images, output, '*/convert/*.nii.gz', outdir_textfield))
    button_box = create_button_box(run_button, show_button)

    return create_panel(html, box1, box2, box3, button_box)


def create_preprocessing_box(output, header):
    html = create_html(header)

    box1, pattern_textfield = create_textfield_box('Input Pattern:', Inputs.preprocessing_input_pattern)
    box2, mni_textfield = create_textfield_box('MNI File:', Inputs.mni)
    box3, outdir_textfield = create_textfield_box('Output Directory:', Inputs.preprocessing_output_dir)

    run_button = widgets.Button(description='Run', button_style='success')
    show_button = widgets.Button(description='Show', button_style='info')
    state = (output, mni_textfield, pattern_textfield, outdir_textfield)
    run_button.on_click(partial(run_preprocessing, *state))
    show_button.on_click(partial(show_images, output, '*/preprocessing/*.nii.gz', outdir_textfield))
    button_box = create_button_box(run_button, show_button)

    return create_panel(html, box1, box2, box3, button_box)


def create_bone_strip_box(output, header):
    html = create_html(header)

    box1, pattern_textfield = create_textfield_box('Input Pattern:', Inputs.bone_strip_input_pattern)
    box2, outdir_textfield = create_textfield_box('Output Directory:', Inputs.bone_strip_output_dir)

    run_button = widgets.Button(description="Run", button_style='success')
    show_button = widgets.Button(description="Show", button_style='info')
    state = (output, pattern_textfield, outdir_textfield)
    run_button.on_click(partial(run_bone_strip, *state))
    show_button.on_click(partial(show_images, output, '*/bone_strip/*.nii.gz', outdir_textfield))
    button_box = create_button_box(run_button, show_button)

    return create_panel(html, box1, box2, button_box)


def create_registration_box(output, header):
    html = create_html(header)

    box1, pattern_textfield = create_textfield_box('Input Pattern:', Inputs.registration_input_pattern)
    box2, template_textfield = create_textfield_box('Template File:', Inputs.template)
    box3, checkboxes = create_checkboxes_box(('a', 's', 'so'))
    box4, outdir_textfield = create_textfield_box('Output Directory:', Inputs.registration_output_dir)

    run_button = widgets.Button(description='Run', button_style='success')
    show_button = widgets.Button(description='Show', button_style='info')
    state = (output, template_textfield, checkboxes, pattern_textfield, outdir_textfield)
    run_button.on_click(partial(run_registration, *state))
    show_button.on_click(partial(show_images, output, '*/registration/*/*.nii.gz', outdir_textfield))
    button_box = create_button_box(run_button, show_button)

    return create_panel(html, box1, box2, box3, box4, button_box)


def create_segmentation_box(output, header):
    html = create_html(header)

    box1, pattern_textfield = create_textfield_box('Input Pattern:', Inputs.segmentation_input_pattern)
    box2, atlas_textfield = create_textfield_box('Atlas File:', Inputs.atlas)
    box3, checkboxes = create_checkboxes_box(('Affine', 'Physical'))
    box4, outdir_textfield = create_textfield_box('Output Directory:', Inputs.segmentation_output_dir)

    run_button = widgets.Button(description='Run', button_style='success')
    show_button = widgets.Button(description='Show', button_style='info')
    state = (output, atlas_textfield, checkboxes, pattern_textfield, outdir_textfield)
    run_button.on_click(partial(run_segmentation, *state))
    show_button.on_click(partial(show_images, output, '*/segmentation/*/*.nii.gz', outdir_textfield))
    button_box = create_button_box(run_button, show_button)

    return create_panel(html, box1, box2, box3, box4, button_box)


def create_geo_box(output, header):
    html = create_html(header)
    box1, pattern_textfield = create_textfield_box('Input Pattern:', Inputs.geo_input_pattern)
    box2, outdir_textfield = create_textfield_box('Output Directory:', Inputs.geo_output_dir)

    run_button = widgets.Button(description="Run", button_style='success')
    show_button = widgets.Button(description="Show", button_style='info')
    state = (output, pattern_textfield, outdir_textfield)
    run_button.on_click(partial(run_label_geometry_measures, *state))
    show_button.on_click(partial(show_csv, output, '*/label_geometry_measures/*.csv', outdir_textfield))
    button_box = create_button_box(run_button, show_button)

    return create_panel(html, box1, box2, button_box)


def create_stat_box(output, header):
    html = create_html(header)
    box1, pattern_textfield = create_textfield_box('Input Pattern:', Inputs.stat_input_pattern)
    box2, atlas_textfield = create_textfield_box('Atlas File:', Inputs.atlas)
    box3, outdir_textfield = create_textfield_box('Output Directory:', Inputs.stat_output_dir)

    run_button = widgets.Button(description='Run', button_style='success')
    show_button = widgets.Button(description='Show', button_style='info')
    state = (output, atlas_textfield, pattern_textfield, outdir_textfield)
    run_button.on_click(partial(run_intensity_stat, *state))
    show_button.on_click(partial(show_csv, output, '*/warp_intensity_stats/*.csv', outdir_textfield))
    button_box = create_button_box(run_button, show_button)

    return create_panel(html, box1, box2, box3, button_box)


__HEADERS__ = (
    """ 
    <h5>Apply these inputs to all workflow steps</h5>
    <ul>
    <li>Input patterns and output directory are automatically derived from this top level output directory</li>
    </ul>
    """,
    """ 
    <h5>Convert a series of .dcm files to .nii.gz files.</h5>
    """,
    """ 
    <h5>Preprocessing process image orientation, voxel size/resolution, bias correction and pre-alignment.</h5>
    """,
    """
    <h5>BoneStrip: strip the bone from CT volume.</h5>
    """,
    """ 
    <h5>Registration: register the bone-stripped CT scan to a template.</h5>
    <ul>
    <li>s:  3 stages rigid + affine + deformable syn </li>
    <li>a:  2 stages rigid + affine</li>
    <li>so: 1 stage deformable syn only</li>
    </ul>
    """,
    """ 
    <h5>Segmentation: segment the bone-stripped CT scan based on a given atlas.</h5>
    <ul>
    <li>Physical: segmentation in the (pre-processed) patient's space</li>
    <li>Affine:   segmentaion in the transformed affine space</li>
    </ul>
    """,
    """ 
    <h5>GeoMeasures: show geometric measures of the segmented regions</h5> 
    <ul>
    <li>volume, area, eccentricity, elongation, orientation</li>
    <li>centroid, axes length, bounding box of the segmented regions</li>
    </ul>
    """,
    """
    <h5>WarpStats: calculate statistics of warp image for each region of the brain.</h5>
    <ul>
    <li>mean, sigma, skewness, kurtosis, entropy, sum, 5th%, 95th%</li>
    </ul>
    """)

__CREATE_FUNCS__ = (create_input_box,
                    create_convert_box,
                    create_preprocessing_box,
                    create_bone_strip_box,
                    create_registration_box,
                    create_segmentation_box,
                    create_geo_box,
                    create_stat_box)

__TITLES__ = ('Inputs',
              'Convert',
              'Preprocessing',
              'BoneStrip',
              'Registration',
              'Segmentation',
              'GeoMeasures',
              'WarpStats')


def display_gui():
    boxes = []

    for idx, create_box in enumerate(__CREATE_FUNCS__):
        layout = widgets.Layout(height='300px', border='2px solid black', overflow_y='scroll')
        output = widgets.Output(layout=layout)
        box = create_box(output, __HEADERS__[idx])
        box = widgets.VBox(children=(box, output))
        boxes.append(box)

    tab = widgets.Tab(children=boxes)

    for idx, title in enumerate(__TITLES__):
        tab.set_title(idx, title)

    display(tab)


display_gui()
