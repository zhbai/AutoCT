############################## 
# Author: Talita Perciano    #
# Aug 2019                   #
##############################

library(neurobase)
library(ichseg)

pathin = '/home/users/tperciano/Dropbox/LBL_Projects/TBI_project/ClinicalCTs/Young_M/Preprocessed/'
pathout = '/home/users/tperciano/Dropbox/LBL_Projects/TBI_project/ClinicalCTs/Young_M/Brains/'

names = list.files(pathin)
for (i in names) {
    if (grepl("normalizedWarped",i)) {
        print(paste("Input: ",i))
        output_name = paste(pathout, unlist(strsplit(i,".",fixed=T))[1], "_brain.nii.gz", sep="")
        print(paste("Output: ",output_name))
        img = readnii(paste(pathin, i, sep=""))
        img = rescale_img(img, min.val = -1024, max.val = 3071)
        print("Finding skull...")
        ss = CT_Skull_Strip(img, verbose = FALSE)
        print("Writing output...")
        writenii(ss, output_name)
    }
}
