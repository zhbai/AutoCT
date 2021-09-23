ARG base_image=python:3.7-slim-stretch
  
FROM ${base_image} AS base

USER root

ARG DEBIAN_FRONTEND="noninteractive"

ENV LANG="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8" 

RUN export ND_ENTRYPOINT="/neurodocker/startup.sh" \
    && apt-get update -qq \
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

ADD docker/ants-2.3.1-bins.tar.gz /opt/ants-2.3.1

ENV PATH="/opt/afni-bins:$PATH" \
    AFNI_PLUGINPATH="/opt/afni-bins"
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           ed \
           gsl-bin \
           libglib2.0-0 \
           libglu1-mesa-dev \
           libglw1-mesa \
           libgomp1 \
           libjpeg62 \
           libxm4 \
           multiarch-support \
           netpbm \
           tcsh \
           xfonts-base \
           xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL --retry 5 -o /tmp/toinstall.deb http://mirrors.kernel.org/debian/pool/main/libx/libxp/libxp6_1.0.2-2_amd64.deb \
    && dpkg -i /tmp/toinstall.deb \
    && rm /tmp/toinstall.deb \
    && curl -sSL --retry 5 -o /tmp/toinstall.deb http://snapshot.debian.org/archive/debian-security/20160113T213056Z/pool/updates/main/libp/libpng/libpng12-0_1.2.49-1%2Bdeb7u2_amd64.deb \
    && dpkg -i /tmp/toinstall.deb \
    && rm /tmp/toinstall.deb \
    && apt-get install -f \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && gsl2_path="$(find / -name 'libgsl.so.19' || printf '')" \
    && if [ -n "$gsl2_path" ]; then \
         ln -sfv "$gsl2_path" "$(dirname $gsl2_path)/libgsl.so.0"; \
    fi \
    && ldconfig 

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

ADD docker/fsl-5.0.10-bins.tar.gz /opt/fsl-5.0.10

ADD docker/dcm2niix.tar.gz /opt/dcm2niix/bin
ENV PATH="/opt/dcm2niix/bin:$PATH" 

ARG autoct_user=autoct
ARG autoct_uid=1000

RUN groupadd \
        --gid ${autoct_uid} \
        ${autoct_user} && \
    useradd \
        --comment "TBI User" \
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

RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && python3 -m pip install --no-cache-dir /build_dir \
    && rm -rf /build_dir \
    && jupyter nbextension enable --py widgetsnbextension

ADD notebooks /notebooks
ADD licence.txt /notebooks/
RUN chown -R ${autoct_user}:${autoct_uid} /notebooks 

RUN echo '#!/bin/bash\n\
echo "*************************************************************"\n\
echo "* Please consult license located at /notebooks/licence.txt. *"\n\
echo "*************************************************************"\n\
exec "$@"\
' > /usr/local/bin/auto_ct_entrypoint.sh && chmod +x /usr/local/bin/auto_ct_entrypoint.sh

ENTRYPOINT ["/usr/local/bin/auto_ct_entrypoint.sh"]
CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
USER ${autoct_user}
WORKDIR /notebooks
