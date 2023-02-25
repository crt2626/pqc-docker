#!/bin/bash

function dependency_install() {

    # Check for and install required packages
    packages=(astyle cmake gcc ninja-build libssl-dev python3-pytest python3-pytest-xdist unzip xsltproc doxygen graphviz python3-yaml valgrind python3-pip)
    not_installed=()
    for package in "${packages[@]}"; do
        if ! dpkg -s "$package" >/dev/null 2>&1; then
            not_installed+=("$package")
        fi
    done
    if [[ ${#not_installed[@]} -ne 0 ]]; then
        apt-get update
        apt-get install -y "${not_installed[@]}"
    fi

}

function download() {

    # Function for setting up the repo
    mkdir /pqc
    mkdir -p /pqc/output 
    mkdir -p /pqc/output/op1
    mkdir -p /pqc/output/op2
    mkdir -p /pqc/output/op3
    cd /pqc
    git clone https://github.com/crt2626/pqc-docker
    cd /pqc/pqc-docker
    git clone https://github.com/open-quantum-safe/liboqs.git
    sudo chown -R $USER /pqc/
    sudo chmod -R 755 /pqc

}

function build() {

    # Function for building and moving liboqs
    cd /pqc/pqc-docker/liboqs
    mkdir build && cd build && cmake .. -DCMAKE_INSTALL_PREFIX=./ && make -j 4 && make install
    cd /pqc/pqc-docker/liboqs
    mv build /pqc/pqc-docker

    # Moving python test script executables folder
    cp /pqc/pqc-docker/scripts/run_mem.py /pqc/pqc-docker/build/tests
    cd ~/
}

echo -e "\nSetting up testing enviroment..."
dependency_install
download
build