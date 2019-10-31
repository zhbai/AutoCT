############################## 
# Author: Talita Perciano    #
# Aug 2019                   #
##############################

scriptsPath=/home/users/tperciano/Dropbox/LBL_Projects/TBI_project/Registration/ANTs/Scripts/
inputPath=/home/users/tperciano/Dropbox/LBL_Projects/TBI_project/ClinicalCTs/Young_F/Templates/158/AverageStart/158_affine
outputPath=${inputPath}/out/

${scriptsPath}/antsMultivariateTemplateConstruction.sh \
  -d 3 \
  -o ${outputPath}T_ \
  -i 4 \
  -g 0.2 \
  -j 40 \
  -c 2 \
  -k 1 \
  -w 1 \
  -m 100x70x50x10 \
  -n 1 \
  -r 1 \
  -s CC \
  -t GR \
  -b 1 \
  ${inputPath}/*.nii.gz

