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
volume onto the docker container. The command below mounts  a `/data` directory.

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
### Example Workflow using illustration data.

The following commands allow you to run all the workflow steps. 
Make sure you use the `-v` option to mount the `/data` directory when using `docker run`
When you are done, the results should be on your host machine in  `DATA_DIR_ON_HOST`.
Also note: the `--rm` option means the container `tbi-reg` would automatically be deleted upon exit

```sh
## Replace  DATA_DIR_ON_HOST with the absolute path to an existing directory on the host machine
## On host machine: 

docker run --rm --name tbi-reg -v DATA_DIR_ON_HOST:/data -it tbi:1.0 /bin/bash

## Inside container:
tbi-convert --use-dcm2niix  'illustration_data/dcmfiles/*' /data/output/convert

tbi-preprocessing -m illustration_data/MNI152_T1_1mm_brain.nii.gz '/data/output/convert/*.nii.gz' \
     /data/output/preprocessing

tbi-skull-strip '/data/output/preprocessing/*.nii.gz' /data/output/skull-strip

tbi-registration -t illustration_data/T_template0.nii.gz \
  '/data/output/skull-strip/*.nii.gz'  /data/output/registration

tbi-segmentation -a illustration_data/New_atlas_cort_asym_sub.nii.gz  \
  '/data/output/registration/*/*.nii.gz'  /data/output/segmentation

tbi-label-geometry-measures '/data/output/segmentation/*/*.nii.gz' /data/output/geometry_measures

tbi-image-intensity-stat -a  illustration_data/New_atlas_cort_asym_sub.nii.gz \
   '/data/output/registration/*/*.nii.gz' /data/output/intensity_stats
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

