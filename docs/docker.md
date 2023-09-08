# AutoCT

## Run AutoCT Scripts Using Docker

### Installation

- These steps were successfully tested using:
    - MacBook Air with 4 CPUs and 16G RAM (10.15.3)
    - Docker (19.03.5)
    
    Note: Docker was given 3 CPUs and 8G RAM. (on mac see Docker Preferences | Resources)

#### AutoCT Repository:

Clone the `AutoCT` repository.

```sh
git clone https://github.com/zhbai/AutoCT.git
cd AutoCT
```

#### Docker Image:

- Docker image is based on `python:3.7.17-slim-bullseye` and has the following installed:
    - Python (3.7)
    - ANTs (2.3.1)
    - FSL (5.0.10)

#### BuildingThe Docker Image:
The build instruction is meant for developers. Users, interested in using the `autoct` software,
can skip to the next section and just pull the `autoct` image from Docker Hub.

```sh
docker build -f docker/Dockerfile -t zhebai/autoct:1.1.2 .
```

#### Pull Docker Image From Dockerhub:

```sh
docker pull zhebai/autoct:1.1.2
docker image list
```

### Run Docker Container

The `docker run` shown below places you inside a container named `autoct-reg`. The -v option is used to mount a host 
volume onto the docker container. The command below mounts  a `/data` directory.

```sh
## Replace  DATA_DIR_ON_HOST with the absolute path to your data on the host machine

docker run --name autoct-reg -v DATA_DIR_ON_HOST:/data -it zhebai/autoct:1.1.2 /bin/bash
ls /data    # Should show contents of DATA_DIR_ON_HOST 

## Extras
docker ps    # run this on a different terminal to list docker containers
docker exec -it autoct-reg /bin/bash  # to open another terminal in container. 

## Workflow tools:
autoct-convert -h
autoct-preprocessing -h
autoct-bone-strip -h
autoct-registration -h
autoct-segmentation -h
autoct-label-geometry-measures -h 
autoct-warp-intensity-stats -h

## Template tools:
autoct-template-command-syn-average -h 
```

### Stop/Restart Container

```sh
CTRL D
docker ps -a  # to  list containers including stopped containers
docker start -ia autoct-reg
```

### Exit/Delete Container

```sh
CTRL D
docker rm -f autoct-reg 
```
### Example Workflow using illustration data.

The following commands allow you to run all the workflow steps. 
Make sure you use the `-v` option to mount the `/data` directory when using `docker run`
When you are done, the results should be on your host machine in  `DATA_DIR_ON_HOST`.
Also note: the `--rm` option means the container `autoct-reg` would automatically be deleted upon exit

```sh
## Replace  DATA_DIR_ON_HOST with the absolute path to an existing directory on the host machine
## On host machine: 

docker run --rm --name autoct-reg -v DATA_DIR_ON_HOST:/data -it zhebai/autoct:1.1.2 /bin/bash

## Inside container:
autoct-convert --use-dcm2niix  'illustration_data/dcmfiles/*' /data/output

autoct-preprocessing -m illustration_data/MNI152_T1.1.2mm_brain.nii.gz '/data/output/*/convert/*.nii.gz' \
     /data/output

autoct-bone-strip '/data/output/*/preprocessing/*.nii.gz' /data/output

autoct-registration -t illustration_data/T_template0.nii.gz \
  '/data/output/*/bone_strip/*.nii.gz' /data/output

autoct-segmentation -a illustration_data/New_atlas_cort_asym_sub.nii.gz  \
  '/data/output/*/registration/*/*.nii.gz' /data/output

autoct-label-geometry-measures '/data/output/*/segmentation/*/*.nii.gz' /data/output

autoct-warp-intensity-stats -a illustration_data/New_atlas_cort_asym_sub.nii.gz \
   '/data/output/*/registration/*/*.nii.gz' /data/output
```

### Running Example Jupyter Notebook

The docker run command below uses the -p option to publish port 8888 on host machine. 
When you run this command,  an http url is shown in the output. 
Use this url in your favorite browser and you should see the example notebook.

Note: the --rm option means the container `autoct-jupyter-example` would be deleted upon exit

```sh
## Replace DATA_DIR_ON_HOST with the absolute path to your data on the host machine
docker run --rm --name autoct-jupyter-example -v DATA_DIR_ON_HOST:/data -p 8888:8888 -it zhebai/autoct:1.1.2
```
