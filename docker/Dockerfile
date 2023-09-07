ARG base_image=python:3.7.17-slim-bullseye
  
FROM ${base_image} AS base

USER root

ARG DEBIAN_FRONTEND="noninteractive"

ENV LANG="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8" 

RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           apt-utils \
           bzip2 \
           ca-certificates \
           curl \
           locales \
           unzip \
           procps \ 
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && update-locale LANG="en_US.UTF-8"

ENV ANTSPATH="/opt/ants-2.3.1" \
    PATH="/opt/ants-2.3.1:$PATH"
RUN echo "Installing  ANTs ..." \
    && mkdir -p /opt/ants-2.3.1

ADD docker/files/ants-2.3.1-bins.tar.gz /opt/ants-2.3.1

ENV FSLDIR="/opt/fsl-5.0.10" \
    PATH="/opt/fsl-5.0.10/bin:$PATH" \
    FSLOUTPUTTYPE="NIFTI_GZ" \
    FSLMULTIFILEQUIT="TRUE" \
    FSLTCLSH="/opt/fsl-5.0.10/bin/fsltclsh" \
    FSLWISH="/opt/fsl-5.0.10/bin/fslwish" \
    FSLLOCKDIR="" \
    FSLMACHINELIST="" \
    FSLREMOTECALL="" \
    FSLGECUDAQ="cuda.q"
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           bc \
           dc \
           file \
           libfontconfig1 \
           libfreetype6 \
           libgl1-mesa-dev \
           libgl1-mesa-dri \
           libglu1-mesa-dev \
           libgomp1 \
           libice6 \
           libxcursor1 \
           libxft2 \
           libxinerama1 \
           libxrandr2 \
           libxrender1 \
           libxt6 \
           sudo \
           wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* 

ADD docker/files/fsl-5.0.10-bins.tar.gz /opt/fsl-5.0.10

ADD docker/files/dcm2niix.tar.gz /opt/dcm2niix/bin
ENV PATH="/opt/dcm2niix/bin:$PATH" 

ARG autoct_user=autoct
ARG autoct_uid=1000

RUN groupadd \
        --gid ${autoct_uid} \
        ${autoct_user} && \
    useradd \
        --create-home \
        --gid ${autoct_uid} \
        --uid ${autoct_uid} \
        --no-log-init \
        --shell /bin/bash \
        ${autoct_user}
#####
# Installing python packages.
###
ADD setup.py /build_dir/
ADD autoct /build_dir/autoct

RUN export SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True && python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && python3 -m pip install --no-cache-dir /build_dir \
    && rm -rf /build_dir \
    && jupyter nbextension enable --py widgetsnbextension

ADD notebooks /notebooks
ADD LICENSE /notebooks/
RUN mkdir -p /data && chown -R ${autoct_user}:${autoct_uid} /notebooks /data

RUN echo '#!/bin/bash\n\
echo "*************************************************************"\n\
echo "* Please consult license located at /notebooks/LICENSE. *"\n\
echo "*************************************************************"\n\
exec "$@"\
' > /usr/local/bin/auto_ct_entrypoint.sh && chmod +x /usr/local/bin/auto_ct_entrypoint.sh

ENTRYPOINT ["/usr/local/bin/auto_ct_entrypoint.sh"]
CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
USER ${autoct_user}
WORKDIR /notebooks
