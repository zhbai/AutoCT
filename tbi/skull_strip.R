library(neurobase)
library(ichseg)

args = commandArgs(trailingOnly=TRUE)
pathin = args[1]
pathout = args[2]
names = list.files(pathin)

for (i in names) {
    if (grepl("normalizedWarped",i)) {
        print(paste("Input: ",i))
        input_name = file.path(pathin, i)
        output_name = file.path(pathout, paste(unlist(strsplit(i,".",fixed=T))[1], "_brain.nii.gz", sep=""))
        print(paste("Input: ", input_name))
        print(paste("Output: ",output_name))
        img = readnii(input_name)
        img = rescale_img(img, min.val = -1024, max.val = 3071)
        print("Finding skull...")
        ss = CT_Skull_Strip(img, verbose = FALSE)
        print("Writing output...")
        writenii(ss, output_name)
    }
}
