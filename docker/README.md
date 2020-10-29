# TBI Registration

## Run TBI Scripts Using Docker

### Installation

- These steps were successfully tested using:
    - MacBook Air with 4 CPUs and 16G RAM (10.15.3)
    - Docker (19.03.5)
    
    Note: Docker was given 3 CPUs and 8G RAM. (on mac see Docker Preferences | Resources)

#### TBI Registration Repository:

Clone the `tbi registration` repository and enter the `tbi_registration` directory:

```sh
git clone git@bitbucket.org:LBL_TBI/tbi_registration.git
cd tbi_registration
```

#### Build Docker Image:

- Docker image is based on `debian:stretch` and has the following installed:
    - Python (3.7.8)
    - ANTs (2.3.1)
    - FSL (5.0.10)
    - AFNI (latest)

```sh
docker build -f docker/Dockerfile -t tbi:1.0 .
docker image list
```

### Run Docker Container

The `docker run` shown below places you inside a container named `tbi-reg`. The -v option is used to mount a host 
volume onto the docker container. The command below mounts the `tbi_registration` repository directory and a `data`
directory.

```sh
## Replace  DATA_DIR_ON_HOST with the absolute path to your data on the host machine

docker run --name tbi-reg -v DATA_DIR_ON_HOST:/data -it tbi:1.0 /bin/bash
ls /data    # Should show contents of DATA_DIR_ON_HOST 

## Extras
docker ps    # run this on a different terminal to list docker containers
docker exec -it tbi-reg /bin/bash  # to open another terminal in container. 

## Workflow tools:
tbi-convert -h
tbi-preprocessing -h
tbi-skull-strip -h
tbi-registration -h
tbi-segmentation -h
tbi-label-geometry-measures -h 
tbi-image-intensity-stat -h

## Template tools:
tbi-template-command-syn-average -h 
```
### Example Workflow

Change tbi-convert's input and output, template file (-t) , mni file (-m), and atlas file (-a)
to run workflow with other data. 

```sh
tbi-convert '/data/BR-1001/*/*/' /data/output/convert

tbi-preprocessing -m /data/MNI152_T1_1mm_brain.nii '/data/output/convert/*.nii' /data/output/preprocessing

tbi-skull-strip '/data/output/preprocessing/*_normalizedWarped.nii.gz' /data/output/skull-strip

tbi-registration -t /data/TemplateYoungM_128.nii.gz \
  '/data/output/skull-strip/*_brain.nii.gz'  /data/output/registration

tbi-segmentation -a /data/New_atlas_cort_asym_sub.nii.gz  \
  '/data/output/registration/*/*.nii.gz'  /data/output/segmentation

tbi-label-geometry-measures '/data/output/segmentation/*/*.nii.gz' /data/output/geometry_measures

tbi-image-intensity-stat-jac  -a /data/New_atlas_cort_asym_sub.nii.gz \
   '/data/output/registration/Affine2SyN/*affine2Syn1Warp.nii.gz' /data/output/intensity_stats

```

### Stop/Restart Container

```sh
CTRL D
docker ps -a  # to  list containers including stopped containers
docker start -ia tbi-reg
```

### Exit/Delete Container

```sh
CTRL D
docker rm -f tbi-reg 
```

### Running Example Python Script Using Docker Command.
The docker run command below runs example.py  which resides in the container's working directory.
To run another script you would need to mount it using the -v option.
Note: the --rm option means the container `tbi-run-example` would be deleted upon exit

```sh
## Replace DATA_DIR_ON_HOST with the absolute path to your data on the host machine
docker run --rm --name tbi-run-example -v DATA_DIR_ON_HOST:/data -t tbi:1.0 python example.py
```

### Running Example Jupyter Notebook

The docker run command below uses the -p option to publish port 8888 on host machine. 
When you run this command,  an http url is shown in the output. 
Use this url in your favorite browser and you should see the example notebook.

Note: the --rm option means the container `tbi-jupyter-example` would be deleted upon exit

```sh
## Replace DATA_DIR_ON_HOST with the absolute path to your data on the host machine
docker run --rm --name tbi-jupyter-example -v DATA_DIR_ON_HOST:/data -p 8888:8888 -it tbi:1.0 
```
### Running On NERSC.

Refer to [this document](./nersc.md) for a detailed description.

### Running Tests:
```sh
## Replace REPO_DIR with the absolute path to tbi repository
docker run --rm  -v REPO_DIR:/tbitesting -w /tbitesting  -it tbi:1.0  pytest tests
```

