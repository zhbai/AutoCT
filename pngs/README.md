# Convert a series of .dcm files to .nii.gz files.


```python
tbi.convert(pattern='illustration_data/dcmfiles/*',
            out_dir=join(output, 'convert'), 
            use_dcm2niix=True)
plot_images(join(output, 'convert', "*.nii.gz"))
```

    Plotting /data/illustration_workflow_output/convert/ID_0eba6ca7-7473dee7c1.nii.gz:shape=(512, 512, 35)



    
![png](output_1_1.png)
    


## Preprocess and strip the skull from CT volume.


```python
tbi.preprocessing(pattern=join(output, 'convert', '*.nii.gz'), 
                  out_dir=join(output, 'preprocessing'),
                  mni_file=mni_file)
tbi.skull_strip(pattern=join(output, 'preprocessing', '*.nii.gz'),
                out_dir=join(output, 'brains'))
plot_images(join(output, 'brains', '*.nii.gz'))
```

    Plotting /data/illustration_workflow_output/brains/ID_0eba6ca7-7473dee7c1_brain.nii.gz:shape=(182, 218, 182)



    
![png](output_3_1.png)
    


## Register the skull-stripped CT scan to a template and segment the skull-stripped CT scan based on a given atlas.


```python
tbi.registration(pattern=join(output, 'brains', '*.nii.gz'), 
                 out_dir=join(output, 'registration'), 
                 template=template_file,
                 transforms=tbi.supported_registration_transforms())
tbi.segmentation(pattern=join(output, 'registration', '*/*.nii.gz'), 
                 out_dir=join(output, 'segmentation'), 
                 atlas=atlas_file,
                 types=tbi.supported_segmentation_types())
plot_images(join(output, 'segmentation', '*/*.nii.gz'))
```

    Plotting /data/illustration_workflow_output/segmentation/PHYSCi/ID_0eba6ca7-7473dee7c1_segmentation_cortical_phy.nii.gz:shape=(182, 218, 182)



    
![png](output_5_1.png)
    


    Plotting /data/illustration_workflow_output/segmentation/AFFINE/ID_0eba6ca7-7473dee7c1_segmentation_cortical_affine.nii.gz:shape=(182, 218, 182)



    
![png](output_5_3.png)
    


##  Show geometric measures of the segmented regions.


```python
tbi.label_geometry_measures(pattern=join(output, 'segmentation', '*/*.nii.gz'), 
                            out_dir=join(output, 'label_geometry_measures'))
plot_csv_files(pattern=join(output, 'label_geometry_measures', '*.csv'))
```

    Plotting csv file /data/illustration_workflow_output/label_geometry_measures/ID_0eba6ca7-7473dee7c1_segmentation_cortical_phy.csv



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Label</th>
      <th>Volume(voxels)</th>
      <th>SurfArea(mm^2)</th>
      <th>Eccentricity</th>
      <th>Elongation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>55729</td>
      <td>13525.000</td>
      <td>0.933144</td>
      <td>2.78163</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>9639</td>
      <td>4083.160</td>
      <td>0.974504</td>
      <td>4.45692</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>22358</td>
      <td>7790.010</td>
      <td>0.956832</td>
      <td>3.44067</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>23640</td>
      <td>6768.400</td>
      <td>0.920145</td>
      <td>2.55377</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>5367</td>
      <td>2243.190</td>
      <td>0.888755</td>
      <td>2.18158</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>110</th>
      <td>111</td>
      <td>6725</td>
      <td>2485.240</td>
      <td>0.952519</td>
      <td>3.28429</td>
    </tr>
    <tr>
      <th>111</th>
      <td>112</td>
      <td>2478</td>
      <td>1096.860</td>
      <td>0.923912</td>
      <td>2.61367</td>
    </tr>
    <tr>
      <th>112</th>
      <td>113</td>
      <td>6472</td>
      <td>2640.710</td>
      <td>0.979900</td>
      <td>5.01284</td>
    </tr>
    <tr>
      <th>113</th>
      <td>114</td>
      <td>3257</td>
      <td>1276.420</td>
      <td>0.815370</td>
      <td>1.72729</td>
    </tr>
    <tr>
      <th>114</th>
      <td>115</td>
      <td>632</td>
      <td>437.771</td>
      <td>0.933716</td>
      <td>2.79318</td>
    </tr>
  </tbody>
</table>
<p>115 rows × 5 columns</p>
</div>


    Plotting csv file /data/illustration_workflow_output/label_geometry_measures/ID_0eba6ca7-7473dee7c1_segmentation_cortical_affine.csv



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Label</th>
      <th>Volume(voxels)</th>
      <th>SurfArea(mm^2)</th>
      <th>Eccentricity</th>
      <th>Elongation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>53257</td>
      <td>13234.300</td>
      <td>0.933252</td>
      <td>2.78379</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>9236</td>
      <td>3970.620</td>
      <td>0.976011</td>
      <td>4.59298</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>21471</td>
      <td>7688.720</td>
      <td>0.960424</td>
      <td>3.59011</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>23605</td>
      <td>6768.190</td>
      <td>0.919040</td>
      <td>2.53701</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>5219</td>
      <td>2171.370</td>
      <td>0.885490</td>
      <td>2.15211</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>110</th>
      <td>111</td>
      <td>6626</td>
      <td>2427.830</td>
      <td>0.952159</td>
      <td>3.27222</td>
    </tr>
    <tr>
      <th>111</th>
      <td>112</td>
      <td>2331</td>
      <td>1062.140</td>
      <td>0.929021</td>
      <td>2.70251</td>
    </tr>
    <tr>
      <th>112</th>
      <td>113</td>
      <td>6449</td>
      <td>2597.250</td>
      <td>0.979598</td>
      <td>4.97589</td>
    </tr>
    <tr>
      <th>113</th>
      <td>114</td>
      <td>3174</td>
      <td>1250.490</td>
      <td>0.822842</td>
      <td>1.75973</td>
    </tr>
    <tr>
      <th>114</th>
      <td>115</td>
      <td>622</td>
      <td>436.662</td>
      <td>0.929991</td>
      <td>2.72048</td>
    </tr>
  </tbody>
</table>
<p>115 rows × 5 columns</p>
</div>


## Calculate statistics of warp image for each region of the brain.


```python
tbi.image_intensity_stat(pattern=join(output, 'registration', '*/*.nii.gz'),
                         out_dir=join(output, 'image_intensity_stat'),
                         atlas=atlas_file)
plot_csv_files(pattern=join(output, 'image_intensity_stat', '*.csv'))
```

    Plotting csv file /data/illustration_workflow_output/image_intensity_stat/ID_0eba6ca7-7473dee7c1_preprocessed_affine2Syn1Warp.csv



<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Label</th>
      <th>Mean</th>
      <th>Sigma</th>
      <th>Skewness</th>
      <th>Kurtosis</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>-0.950684</td>
      <td>0.783315</td>
      <td>-1.317570</td>
      <td>-8928.000000</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>-1.305690</td>
      <td>0.855561</td>
      <td>-0.939297</td>
      <td>-1342.600000</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>-0.300798</td>
      <td>0.398898</td>
      <td>-0.167049</td>
      <td>254.040000</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>-0.351033</td>
      <td>0.319761</td>
      <td>0.279979</td>
      <td>1217.160000</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>-0.672450</td>
      <td>0.241615</td>
      <td>-0.910339</td>
      <td>-640.727000</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>110</th>
      <td>111</td>
      <td>-1.287570</td>
      <td>0.425388</td>
      <td>-0.028257</td>
      <td>22.481700</td>
    </tr>
    <tr>
      <th>111</th>
      <td>112</td>
      <td>-1.286590</td>
      <td>0.266363</td>
      <td>0.025636</td>
      <td>-0.116969</td>
    </tr>
    <tr>
      <th>112</th>
      <td>113</td>
      <td>-0.919305</td>
      <td>0.332906</td>
      <td>0.038028</td>
      <td>62.678000</td>
    </tr>
    <tr>
      <th>113</th>
      <td>114</td>
      <td>-1.726520</td>
      <td>0.273731</td>
      <td>-0.287825</td>
      <td>-51.701000</td>
    </tr>
    <tr>
      <th>114</th>
      <td>115</td>
      <td>-1.792370</td>
      <td>0.133691</td>
      <td>-0.071940</td>
      <td>7.653460</td>
    </tr>
  </tbody>
</table>
<p>115 rows × 5 columns</p>
</div>

