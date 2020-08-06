library(neurobase)
library(ichseg)

args = commandArgs(trailingOnly=TRUE)
input_name = args[1]
print(paste("Input: ", input_name))
pathout = args[2]
prefix = unlist(strsplit(basename(input_name),"_normalizedWarped",fixed=T))[1]
print(paste("Prefix: ", prefix))
output_name = file.path(pathout, paste(prefix, "_brain.nii.gz", sep=""))
print(paste("Output: ",output_name))
img = readnii(input_name)
img = rescale_img(img, min.val = -1024, max.val = 3071)
print("Finding skull...")
ss = CT_Skull_Strip(img, verbose = FALSE)
print("Writing output...")
writenii(ss, output_name)
