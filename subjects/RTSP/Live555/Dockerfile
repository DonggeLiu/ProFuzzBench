FROM ubuntu:16.04

ARG USR
ARG PSW
ARG UID
ARG GID

RUN echo "Github User    : $USR" \
    && echo "Github Password: $PSW" \
    && echo "Host User ID : $UID" \
    && echo "Host Group ID: $GID"


# Install common dependencies
RUN apt-get -y update && \
    apt-get -y install sudo \ 
    apt-utils \
    build-essential \
    openssl \
    clang \
    graphviz-dev \
    git \
    libgnutls-dev \
    python-pip \
    nano \
    net-tools \
    vim

# Install dependencies for AFLNet_Legion
RUN cp /etc/apt/sources.list /etc/apt/sources.list~ \
    && sed -Ei 's/^# deb-src /deb-src /' /etc/apt/sources.list \
    && sed -ri '/^# deb-src .* xenial(-updates){0,1} main restricted$/s/^# //g' /etc/apt/sources.list \
    && apt update \
    && apt -y install libglib2.0-dev cmake vim tzdata gdb libc6-dbg dpkg-dev libgnutls28-dev \
    && mkdir -p /opt/src \
    && cd /opt/src \
    && apt source libc6 \
    && mkdir -p /build/glibc-e6zv40/ \
    && ln -s /opt/src/glibc-2.23 /build/glibc-e6zv40/

# Set the timezone of docker for AFLNet_Legion loggings
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime
ENV TZ=Australia/Melbourne

# Add a new user ubuntu, pass: ubuntu
RUN groupadd -o -g $GID ubuntu && \
    useradd -rm -d /home/ubuntu -s /bin/bash -G sudo -o -u $UID -g $GID ubuntu -p "$(openssl passwd -1 ubuntu)"

# Use ubuntu as default username
USER ubuntu
WORKDIR /home/ubuntu

# Download and compile AFLNet
ENV LLVM_CONFIG="llvm-config-3.8"

# Set up fuzzers
RUN git clone https://github.com/Alan32Liu/aflnet.git && \
    cd aflnet && \
    make clean all && \
    cd llvm_mode && make

RUN git clone https://github.com/profuzzbench/aflnwe.git && \
    cd aflnwe && \
    make clean all && \
    cd llvm_mode && make

# Set up AFLNet_Legion
RUN git clone https://${USR}:${PSW}@github.com/Alan32Liu/AFLNet_Legion.git aflnet_legion && \
    cd aflnet_legion && \
    make clean all && \
    cd llvm_mode && make

# Set up environment variables for AFLNet
ENV WORKDIR="/home/ubuntu/experiments"
ENV AFLNET="/home/ubuntu/aflnet"
ENV PATH="${PATH}:${AFLNET}:/home/ubuntu/.local/bin:${WORKDIR}"
ENV AFL_PATH="${AFLNET}"
ENV AFL_NET="${AFLNET}"

ENV AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1 \
    AFL_SKIP_CPUFREQ=1 \
    AFL_NO_AFFINITY=1

RUN mkdir $WORKDIR && \
    pip install gcovr

COPY --chown=ubuntu:ubuntu fuzzing.patch ${WORKDIR}/fuzzing.patch
COPY --chown=ubuntu:ubuntu gcov.patch ${WORKDIR}/gcov.patch
COPY --chown=ubuntu:ubuntu kill-server.sh ${WORKDIR}/kill-server
COPY --chown=ubuntu:ubuntu in-rtsp ${WORKDIR}/in-rtsp
COPY --chown=ubuntu:ubuntu rtsp.dict ${WORKDIR}/rtsp.dict
COPY --chown=ubuntu:ubuntu cov_script.sh ${WORKDIR}/cov_script
COPY --chown=ubuntu:ubuntu run.sh ${WORKDIR}/run
    

# Download and compile Live555 for fuzzing
RUN cd $WORKDIR && \
    git clone https://github.com/rgaufman/live555.git && \
    cd live555 && \
    git checkout ceeb4f4 && \
    patch -p1 < $WORKDIR/fuzzing.patch && \
    ./genMakefiles linux && \
    make clean all

# Set up Live555 for fuzzing
RUN cd ${WORKDIR}/live555/testProgs && \
    cp ${AFLNET}/tutorials/live555/sample_media_sources/*.* ./

# Download and compile Live555 for coverage analysis
RUN cd $WORKDIR && \
    git clone https://github.com/rgaufman/live555.git live555-cov && \
    cd live555-cov && \
    git checkout ceeb4f4 && \
    patch -p1 < $WORKDIR/gcov.patch && \
    ./genMakefiles linux && \
    make CFLAGS="-fprofile-arcs -ftest-coverage" CPPFLAGS="-fprofile-arcs -ftest-coverage" CXXFLAGS="-fprofile-arcs -ftest-coverage" LDFLAGS="-fprofile-arcs -ftest-coverage" clean all

# Set up Live555 for coverage analysis
RUN cd ${WORKDIR}/live555-cov/testProgs && \
    cp ${AFLNET}/tutorials/live555/sample_media_sources/*.* ./

# Download the scripts to process results
RUN git clone https://${USR}:${PSW}@github.com/Alan32Liu/diff-gcov.git