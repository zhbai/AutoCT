# AutoCT

## Run AutoCT Scripts Using Shifter And Jupyer on NERSC

- Useful links.
    - SSH to NERSC using [sshproxy](https://docs.nersc.gov/connect/mfa/#mfa-for-ssh-keys-sshproxy) 
    - Using [Shifter](https://docs.nersc.gov/development/shifter/how-to-use/)
    - Shifter Kernels On [Jupyter](https://docs.nersc.gov/services/jupyter/)

### Build And Push Image to NERSC's Registry

```sh
git clone git@bitbucket.org:LBL_TBI/tbi_registration.git
cd tbi_registration
docker build -f docker/Dockerfile -t autoct:1.0 .
export NERSC_USERNAME=????
docker login registry.services.nersc.gov
docker tag autoct:1.0 registry.services.nersc.gov/$NERSC_USERNAME/autoct:1.0
docker push registry.services.nersc.gov/$NERSC_USERNAME/autoct:1.0 
```

### Pull Image And Run On Login Node

```sh
ssh -i ~/.ssh/nersc $NERSC_USERNAME@cori.nersc.gov
shifterimg pull registry.services.nersc.gov/$USER/autoct:1.0
export DATA_ON_NERSC=????
shifter --image=registry.services.nersc.gov/$USER/autoct:1.0 --volume=$DATA_ON_NERSC:/data /bin/bash
autoct-template-command-syn-average -h
```

### Pull Image And Run On Compute Node

Adjust the time (-t) depending on what you are planning to do. 

```sh
ssh -i ~/.ssh/nersc $NERSC_USERNAME@cori.nersc.gov
shifterimg  pull registry.services.nersc.gov/$USER/autoct:1.0
export DATA_ON_NERSC=????
salloc -N 1 -C haswell -q interactive -t 01:00:00 --image=registry.services.nersc.gov/$USER/autoct:1.0 \
  --volume=$DATA_ON_NERSC:/data
shifter /bin/bash
ls /data 
autoct-template-command-syn-average -h
autoct-template-command-syn-average -i /data/skulls /data/template-2
```

### USING NERSC's Jupyter

First ssh to Cori, create an environment `autoct-env` by placing a kernel file under `~/.local/share/jupyter/kernels/autoct-env/kernel.json`. A sample kernel json file is shown below. 
Need to update the image name and use 'shifterimg  pull' to test it.

Login to [Jupyter](https://jupyter.nersc.gov) and use Cori's shared cpu nodes/exclusive nodes.  When creating 
notebooks be sure to specify `autoct-env`.

```json
{
 "argv": [
     "shifter", 
      "--image=UPDATE_ME",
      "/usr/local/bin/python",
      "-m",
      "ipykernel_launcher",
      "-f",
      "{connection_file}"
 ],
 "display_name": "autoct-env",
 "language": "python"
}
```

