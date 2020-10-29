#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from IPython.display import display
import ipywidgets as widgets
import tbi

from glob import glob
import nilearn.plotting as plotting
import pandas as pd
from os.path import join
from functools import partial
import os.path

class ImageViewer:
    def __init__(self, filename):
        self.filename = filename
       
    @classmethod
    def create_slider(cls, value, amin, amax, direction):
        return widgets.IntSlider(value=value,
                                 min=amin, 
                                 max=amax, 
                                 step=1, 
                                 continuous_update=False, 
                                 description=direction)
    
    @classmethod
    def create_layout(cls, height='200px', border='4px solid blue', overflow_y='scroll'):
        return widgets.Layout(height=height, border=border, overflow_y=overflow_y)
    
    def display_image(self, output):
        from nilearn.plotting.find_cuts import find_cut_slices
        
        img = tbi.load_as_3d(self.filename)
        self.update = 0
        n_cuts = 7
        axes = ('x', 'y', 'z')
        all_cuts = [find_cut_slices(img, n_cuts=n_cuts, direction=axis) for axis in axes]
        self.img = img
        self.sliders = []
        for i, axis in enumerate(axes):
            cuts = all_cuts[i]
            value, amin, amax = cuts[int(n_cuts/2)] , cuts.min(),  cuts.max()
            self.sliders.append(self.create_slider(value, amin, amax, axis))
            
        children = [widgets.interactive(self._plot_slice, view=slider) for slider in self.sliders]  
        self.out = widgets.Output(layout=self.create_layout())
        box = widgets.VBox(children=[widgets.HBox(children=children), 
                                     widgets.HBox(children=[create_space_box(), 
                                                            self.out])
                                    ])
        self.outer_output = output
        display(box)
    
    def _plot_slice(self, view):
        self.update += 1
        
        if self.update < 3:
            return
        
        with self.outer_output:
            with self.out:
                self.out.clear_output()
                cut_coords = tuple(slider.value for slider in self.sliders)
                plotting.plot_img(self.img, display_mode='ortho', cut_coords=cut_coords)
                plotting.show()

def display_image(nii_file, output=None, use_viewer=True):
    print('Plotting {0}'.format(nii_file))
    if use_viewer:
        assert output != None
        viewer = ImageViewer(nii_file)
        viewer.display_image(output)
    else:
        plotting.plot_img(nii_file)
        plotting.show()
        
                
class Inputs:
    _outdir = '/data/illustration_output'
    _mni = 'illustration_data/MNI152_T1_1mm_brain.nii.gz'
    _atlas = 'illustration_data/New_atlas_cort_asym_sub.nii.gz'
    _template = 'illustration_data/T_template0.nii.gz'
    
    dcmfiles = 'illustration_data/dcmfiles/*/'
    _cache = {}

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
        textfields = cls._cache.get(key)
        
        if textfields is None:
            textfields = [textfield]
            cls._cache[key] = textfields
        else:
            textfields.append(textfield)
    
    @classmethod
    def convert_input_pattern(cls):
        return cls.dcmfiles
    
    @classmethod
    def convert_output_dir(cls):
        return os.path.join(cls.outdir(), 'convert')

    @classmethod
    def preprocessing_input_pattern(cls, pattern='*.nii.gz'):
        return os.path.join(cls.convert_output_dir(), pattern)

    @classmethod
    def preprocessing_output_dir(cls):
        return os.path.join(cls.outdir(), 'preprocessing')
    
    @classmethod
    def skull_strip_input_pattern(cls, pattern='*_normalizedWarped.nii.gz'):
        return os.path.join(cls.preprocessing_output_dir(), pattern)
    
    @classmethod
    def skull_strip_output_dir(cls):
        return os.path.join(cls.outdir(), 'brains')
    
    @classmethod
    def registration_input_pattern(cls, pattern='*.nii.gz'):
        return os.path.join(cls.skull_strip_output_dir(), pattern)
    
    @classmethod
    def registration_output_dir(cls):
        return os.path.join(cls.outdir(), 'registration')
    
    @classmethod
    def segmentation_input_pattern(cls, pattern='*/*.nii.gz'):
        return os.path.join(cls.registration_output_dir(), pattern)

    @classmethod
    def segmentation_output_dir(cls):
        return os.path.join(cls.outdir(), 'segmentation')
    
    @classmethod
    def geo_input_pattern(cls, pattern='*/*.nii.gz'):
        return os.path.join(cls.segmentation_output_dir(), pattern)

    @classmethod
    def geo_output_dir(cls):
        return os.path.join(cls.outdir(), 'label_geometry_measures')
    
    @classmethod
    def stat_input_pattern(cls, pattern='Affine2SyN/*affine2Syn1Warp.nii.gz'):
        return os.path.join(cls.registration_output_dir(), pattern)

    @classmethod
    def stat_output_dir(cls):
        return os.path.join(cls.outdir(), 'image_intensity_stat')

def create_html(text, layout=widgets.Layout(height='45px', width='90%', size='20')):
    space_box = widgets.Box(layout=widgets.Layout(height ='25px', width='90%')) 
    return widgets.Box([widgets.HTML(text, layout=layout), space_box])
    
def create_textfield(value, layout=widgets.Layout(width = "60%")):
    textfield = widgets.Text(layout=layout)
    
    if callable(value):
        textfield.value = value()
        Inputs.to_cache(value, textfield)
    else:
        textfield.value = value
        
    return textfield

def create_checkbox(description):
    return widgets.Checkbox(value=False, description=description, disabled=False, indent=False)
    
def create_label(value, layout=widgets.Layout(width = '18%')):
    return widgets.Label(value=value, layout=layout)

def create_checkbox_box(description):
    checkbox = create_checkbox(description)
    box = widgets.Box([create_label(''), checkbox])
    return box, checkbox
    
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
    
    temp.append(widgets.Box(layout=widgets.Layout(height ='4px')))
    temp.append(buttons)
    temp.append(widgets.Box(layout=widgets.Layout(height ='3px')))
    return widgets.VBox(children=temp)

def apply_inputs(out, output_dir_textfield, template_textfield, atlas_textfield, mni_textfield, b):
    out.clear_output()
    
    with out:
        Inputs._outdir = output_dir_textfield.value
        Inputs._template = template_textfield.value
        Inputs._atlas = atlas_textfield.value
        Inputs._mni = mni_textfield.value
       
        for func, lst in Inputs._cache.items():
            for textfield in lst:
                textfield.value = func()
        
def run_convert(output, pattern_textfield, use_dcm2niix_checkbox, output_dir_textfield, b):
    output.clear_output()
   
    with output:
        tbi.convert(pattern_textfield.value, 
                    output_dir_textfield.value, 
                    use_dcm2niix=use_dcm2niix_checkbox.value)

    
def show_images(output, pattern, output_dir_textfield, b):
    output.clear_output()
    
    with output:
        nii_files = glob(join(output_dir_textfield.value, pattern))
        
        for nii_file in nii_files:
            display_image(nii_file, output)
            
def show_csv(output, pattern, output_dir_textfield, b):
    output.clear_output()
    with output:
        csv_files = glob(join(output_dir_textfield.value, pattern))

        for csv_file in csv_files:
            print('Displaying csv file', csv_file)
            df = pd.read_csv(csv_file)
            display(df)

def run_preprocessing(output, mni_textfield, 
                           pattern_textfield, 
                           output_dir_textfield, 
                           b):
    output.clear_output()
    with output:
        tbi.preprocessing(pattern_textfield.value, 
                          output_dir_textfield.value, 
                          mni_textfield.value)

def run_skull_strip(output, pattern_textfield, output_dir_textfield, b):
    output.clear_output()
    
    with output:
        tbi.skull_strip(pattern_textfield.value, output_dir_textfield.value)

def run_registration(output,
                     template_textfield, 
                     pattern_textfield, 
                     output_dir_textfield, 
                     run_button):
    output.clear_output()
    with output:
        tbi.registration(pattern_textfield.value, 
                 output_dir_textfield.value, 
                 template_textfield.value)

def run_segmentation(output, atlas_textfield, 
                     pattern_textfield, 
                     output_dir_textfield, 
                     run_button):
    output.clear_output()
    with output:
        tbi.segmentation(pattern_textfield.value, 
                         output_dir_textfield.value,
                         atlas_textfield.value)
            
def run_label_geometry_measures(output, pattern_textfield, output_dir_textfield, b):
    output.clear_output()
    with output:
        tbi.label_geometry_measures(pattern_textfield.value, 
                                    output_dir_textfield.value)

def run_intensity_stat(output, atlas_textfield, 
                           pattern_textfield, 
                           output_dir_textfield, 
                           run_button):
    output.clear_output()
    with output:
        tbi.image_intensity_stat(pattern_textfield.value,
                                 output_dir_textfield.value,
                                 atlas_textfield.value)
                                 
def create_input_box(output, header):
    html = create_html(header)
    
    box1, outdir_textfield = create_textfield_box('Ouput Directory:', Inputs.outdir())
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
    show_button.on_click(partial(show_images, output, '*.nii.gz', outdir_textfield))
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
    show_button.on_click(partial(show_images, output, '*.nii.gz', outdir_textfield))
    button_box = create_button_box(run_button, show_button)
    
    return create_panel(html, box1, box2, box3, button_box)

def create_skull_strip_box(output, header):
    html = create_html(header)
    
    box1, pattern_textfield = create_textfield_box('Input Pattern:', Inputs.skull_strip_input_pattern)
    box2, outdir_textfield = create_textfield_box('Output Directory:', Inputs.skull_strip_output_dir)

    run_button = widgets.Button(description="Run", button_style='success')
    show_button = widgets.Button(description="Show", button_style='info')
    state = (output, pattern_textfield, outdir_textfield)
    run_button.on_click(partial(run_skull_strip, *state))
    show_button.on_click(partial(show_images, output, '*.nii.gz', outdir_textfield))
    button_box = create_button_box(run_button, show_button)

    return create_panel(html, box1, box2, button_box)

def create_registration_box(output, header):
    html = create_html(header)
    
    box1, pattern_textfield = create_textfield_box('Input Pattern:', Inputs.registration_input_pattern)
    box2, template_textfield = create_textfield_box('Template File:', Inputs.template)
    box3, outdir_textfield = create_textfield_box('Output Directory:', Inputs.registration_output_dir)

    run_button = widgets.Button(description='Run', button_style='success')
    show_button = widgets.Button(description='Show', button_style='info')
    state = (output, template_textfield, pattern_textfield, outdir_textfield)
    run_button.on_click(partial(run_registration, *state))
    show_button.on_click(partial(show_images, output, '*/*.nii.gz', outdir_textfield))
    button_box = create_button_box(run_button, show_button)
    
    return create_panel(html, box1, box2, box3, button_box)

def create_segmentation_box(output, header):
    html = create_html(header)
    
    box1, pattern_textfield = create_textfield_box('Input Pattern:', Inputs.segmentation_input_pattern)
    box2, atlas_textfield = create_textfield_box('Atlas File:', Inputs.atlas)
    box3, outdir_textfield = create_textfield_box('Output Directory:', Inputs.segmentation_output_dir)

    run_button = widgets.Button(description='Run', button_style='success')
    show_button = widgets.Button(description='Show', button_style='info')
    state = (output, atlas_textfield, pattern_textfield, outdir_textfield)
    run_button.on_click(partial(run_segmentation, *state))
    show_button.on_click(partial(show_images, output, '*/*.nii.gz', outdir_textfield))
    button_box = create_button_box(run_button, show_button)
    
    return create_panel(html, box1, box2, box3, button_box)

def create_geo_box(output, header):
    html = create_html(header)
    box1, pattern_textfield = create_textfield_box('Input Pattern:', Inputs.geo_input_pattern)
    box2, outdir_textfield = create_textfield_box('Output Directory:', Inputs.geo_output_dir)

    run_button = widgets.Button(description="Run", button_style='success')
    show_button = widgets.Button(description="Show", button_style='info')
    state = (output, pattern_textfield, outdir_textfield)
    run_button.on_click(partial(run_label_geometry_measures, *state))
    show_button.on_click(partial(show_csv, output, '*.csv', outdir_textfield))
    button_box = create_button_box(run_button, show_button)

    return create_panel(html, box1, box2, button_box)

def create_stat_box(output, header):
    #html = create_html("""Image Intensity Stat Jac uses results from REGIS/Affine2SyN""")
    html = create_html(header)
    box1, pattern_textfield = create_textfield_box('Input Pattern:', Inputs.stat_input_pattern)
    box2, atlas_textfield = create_textfield_box('Atlas File:', Inputs.atlas)
    box3, outdir_textfield = create_textfield_box('Output Directory:', Inputs.stat_output_dir)

    run_button = widgets.Button(description='Run', button_style='success')
    show_button = widgets.Button(description='Show', button_style='info')
    state = (output, atlas_textfield, pattern_textfield, outdir_textfield)
    run_button.on_click(partial(run_intensity_stat, *state))
    show_button.on_click(partial(show_csv, output, '*.csv', outdir_textfield))
    button_box = create_button_box(run_button, show_button)
    
    return create_panel(html, box1, box2, box3, button_box)

__HEADERS__ = (
    """ 
    Input: input a series of .dcm files.
    """,
    """ 
    Convert: convert .dcm files to .nii files.
    """,
    """ 
    Preprocessing: process image orientation, voxel size/resolution, bias correction and pre-alignment.
    """,
    """
    SkullStrip: strip the skull from CT volume.
    """,
    """ 
    Registration: register the skull-stripped CT scan to a template.
    - 3 stages: rigid + affine + deformable syn.
    - 2 stages: rigid + affine.
    - 1 stage: deformable syn only.
    """,
    """ 
    Segmentation: segment the skull-stripped CT scan based on a given atlas.
    - Physical: segmentation in the (pre-processed) patient's space.
    - Affine: segmentaion in the transformed affine space.
    """,
    """ 
    GeoMeasures: show geometric measures (volume, area, eccentricity, elongation, orientation, centroid, axes length, bounding box) of the segmented regions.
    """,
    """
    WarpStats: calculate statistics (mean, sigma, skewness, kurtosis, entropy, sum, 5th%, 95th%) of warp image for each region of the brain.
    """)

__CREATE_FUNCS__ = (create_input_box, 
                create_convert_box,
                create_preprocessing_box,
                create_skull_strip_box,
                create_registration_box,
                create_segmentation_box,
                create_geo_box,
                create_stat_box)

__TITLES__ = ('Inputs', 
          'Convert', 
          'Preprocessing', 
          'SkullStrip', 
          'Registration',
          'Segmentation', 
          'GeoMeasures', 
          'WarpStats')

def display_gui():
    boxes = []

    for idx, create_box in enumerate(__CREATE_FUNCS__): 
        layout=widgets.Layout(height='300px', border='2px solid black', overflow_y='scroll')
        output = widgets.Output(layout=layout)
        box = create_box(output, __HEADERS__[idx])
        box = widgets.VBox(children=(box, output))
        boxes.append(box)

    tab = widgets.Tab(children=boxes)

    for idx, title in enumerate(__TITLES__):
        tab.set_title(idx, title)
    
    display(tab)

display_gui()

# In[ ]:




