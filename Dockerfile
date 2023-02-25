FROM debian:bullseye

# Default location where all binaries wind up:
ARG INSTALLDIR=/pqc/pqc-docker
ARG BUILDDIR=/pqc/pqc-docker/build

# liboqs build defines (https://github.com/open-quantum-safe/liboqs/wiki/Customizing-liboqs)
ARG LIBOQS_BUILD_DEFINES=""

# Define the degree of parallelism when building the image
ARG MAKE_DEFINES="-j 8"

ENV DEBIAN_FRONTEND noninteractive

# Get all software packages required for building liboqs
RUN apt-get update && \
    apt-get install -y \
    astyle \
    build-essential \
    cmake \
    gcc \
    graphviz \
    libssl-dev \
    ninja-build \
    python3-pytest \
    python3-pytest-xdist \
    python3-yaml \
    sudo \
    unzip \
    valgrind \
    vim \
    nano \
    iproute2 \
    python3 \
    xsltproc \
    doxygen \ 
    git

#Setting root password
RUN echo 'root:password' | chpasswd

# create a user with root privileges
RUN useradd --no-log-init --system --uid 1000 --create-home testuser

# Setting up testing directories
WORKDIR /pqc/
RUN mkdir -p /pqc/output
RUN mkdir -p /pqc/output/op1
RUN mkdir -p /pqc/output/op2
RUN mkdir -p /pqc/output/op3
RUN git clone https://github.com/crt2626/pqc-docker.git
RUN mkdir -p /pqc/pqc-docker/bin
RUN cp /pqc/pqc-docker/scripts/run_mem.py /pqc/pqc-docker/bin/
WORKDIR /pqc/pqc-docker/
RUN git clone https://github.com/open-quantum-safe/liboqs.git
RUN chown -R testuser /pqc/
RUN chmod -R 755 /pqc

# switch to the new user
USER testuser

# Setting up build
WORKDIR /pqc/pqc-docker/liboqs
RUN mkdir build && cd build && cmake .. ${LIBOQS_BUILD_DEFINES} -DCMAKE_INSTALL_PREFIX=${INSTALLDIR} && make ${MAKE_DEFINES} && make install
WORKDIR /pqc/pqc-docker/liboqs
RUN mv build /pqc/pqc-docker/
WORKDIR /pqc/pqc-docker/scripts
RUN cp run_mem.py /pqc/pqc-docker/build/tests/

WORKDIR /home/testuser
#CMD ["/pqc/pqc-docker/scripts/run-tests.sh"]