FROM aiplanning/planutils:latest

# Install system tools and Java JDK (headless is sufficient for compiling and running ENHSP)
RUN apt-get update && apt-get install -y \
    bc \
    git \
    cmake \
    build-essential \
    bison \
    flex \
    wget \
    patch \
    openjdk-17-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

# Install solvers and tools via planutils
RUN planutils install -y val
RUN planutils install -y ff
RUN planutils install -y metric-ff
RUN planutils install -y popf
RUN planutils install -y optic
RUN planutils install -y tfd
RUN planutils install -y downward
RUN planutils install -y panda

# Install and build ENHSP
RUN mkdir -p /opt/enhsp && \
    wget https://gitlab.com/enricos83/ENHSP-Public/-/archive/master/ENHSP-Public-master.tar.gz -O /tmp/enhsp.tar.gz && \
    tar -xzf /tmp/enhsp.tar.gz -C /opt/enhsp --strip-components=1 && \
    rm /tmp/enhsp.tar.gz && \
    cd /opt/enhsp && \
    chmod +x compile && \
    ./compile && \
    printf '#!/bin/sh\nexec java -jar /opt/enhsp/enhsp.jar "$@"\n' > /usr/local/bin/enhsp && \
    chmod +x /usr/local/bin/enhsp

# Install and build Lilotane
RUN git clone https://github.com/domschrei/lilotane.git /opt/lilotane

WORKDIR /opt/lilotane

# Fix missing includes for newer GCC versions
RUN sed -i '/#include <algorithm>/a #include <limits>' src/util/robin_hood.h && \
    sed -i '/#include "algo\/plan_writer.h"/a #include <optional>' src/algo/planner.h && \
    sed -i '/#include <vector>/a #include <cstddef>' src/sat/binary_amo.h

# Lilotane's Glucose helper downloads from a DNS-fragile Labri URL. Use a
# GitHub mirror of the same glucose-syrup-4.1 source layout instead.
RUN sed -i '2i set -e' lib/glucose4/fetch_and_build.sh && \
    sed -i 's|wget www.labri.fr/perso/lsimon/downloads/softwares/glucose-syrup-4.1.tgz|git clone --depth 1 https://github.com/hriener/glucose-syrup-4.1.git glucose-src|' lib/glucose4/fetch_and_build.sh && \
    sed -i '/tar xzvf glucose-syrup-4.1.tgz/d' lib/glucose4/fetch_and_build.sh && \
    sed -i 's|mv glucose-syrup-4.1 glucose-4|mv glucose-src/glucose glucose-4 \&\& rm -rf glucose-src|' lib/glucose4/fetch_and_build.sh

RUN mkdir -p build && \
    cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=RELEASE -DIPASIRSOLVER=glucose4 && \
    make

# Make Lilotane executable globally available
RUN ln -s /opt/lilotane/build/lilotane /usr/local/bin/lilotane

# Modify the configuration file to enable hostfs, i.e. use the host file system
RUN perl -pi.bak -e "s/mount hostfs = no/mount hostfs = yes/g" /etc/apptainer/apptainer.conf

WORKDIR /project

CMD ["/bin/bash"]cd