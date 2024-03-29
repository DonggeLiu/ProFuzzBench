FROM ubuntu:18.04

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
    libgnutls28-dev \
    python-pip \
    nano \
    net-tools \
    vim \
    bison \
    flex \
    autotools-dev autoconf automake libtool gettext gawk \
    gperf antlr3 libantlr3c-dev libconfuse-dev libunistring-dev libsqlite3-dev \
    libavcodec-dev libavformat-dev libavfilter-dev libswscale-dev libavutil-dev \
    libasound2-dev libmxml-dev libgcrypt20-dev libavahi-client-dev zlib1g-dev \
    libevent-dev libplist-dev libsodium-dev libjson-c-dev libwebsockets-dev \
    libcurl4-openssl-dev avahi-daemon

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
RUN groupadd -g $GID ubuntu && \
    useradd -rm -d /home/ubuntu -s /bin/bash -G sudo -u $UID -g $GID ubuntu -p "$(openssl passwd -1 ubuntu)"

# Use ubuntu as default username
USER ubuntu
WORKDIR /home/ubuntu

# Download and compile AFLNet
ENV LLVM_CONFIG="llvm-config-6.0"

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
ENV AFLNET_LEGION_LOG='/home/ubuntu/aflnet_legion/log.ansi'

ENV AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1 \
    AFL_SKIP_CPUFREQ=1 \
    AFL_NO_AFFINITY=1

RUN mkdir $WORKDIR && \
    pip install gcovr

COPY --chown=ubuntu:ubuntu forked-daapd.patch ${WORKDIR}/forked-daapd.patch
COPY --chown=ubuntu:ubuntu forked-daapd-gcov.patch ${WORKDIR}/forked-daapd-gcov.patch
COPY --chown=ubuntu:ubuntu in-daap ${WORKDIR}/in-daap
COPY --chown=ubuntu:ubuntu cov_script.sh ${WORKDIR}/cov_script
COPY --chown=ubuntu:ubuntu run.sh ${WORKDIR}/run
COPY --chown=ubuntu:ubuntu MP3 ${WORKDIR}/MP3
COPY --chown=ubuntu:ubuntu forked-daapd.conf ${WORKDIR}/forked-daapd.conf


# Download and compile forked-daapd for fuzzing
RUN cd $WORKDIR && \
    git clone https://github.com/ejurgensen/forked-daapd.git && \
    cd forked-daapd && \
    git checkout 2ca10d9 && \
    patch -p1 < $WORKDIR/forked-daapd.patch && \
    autoreconf -i && \
    CC=$AFLNET/afl-clang-fast CFLAGS="-DSQLITE_CORE" ./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var  --disable-mpd --disable-itunes --disable-lastfm --disable-spotify --disable-verification  --disable-shared --enable-static && \
    make clean all


# Download and compile forked-daapd for code coverage analysis
RUN cd $WORKDIR && \
    git clone https://github.com/ejurgensen/forked-daapd.git forked-daapd-gcov && \
    cd forked-daapd-gcov && \
    git checkout 2ca10d9 && \
    patch -p1 < $WORKDIR/forked-daapd.patch && \
    patch -p1 < $WORKDIR/forked-daapd-gcov.patch && \
    autoreconf -i && \
    CFLAGS="-DSQLITE_CORE -fprofile-arcs -ftest-coverage" LDFLAGS="-fprofile-arcs -ftest-coverage" ./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var  --disable-mpd --disable-itunes --disable-lastfm --disable-spotify --disable-verification  --disable-shared --enable-static && \
    make clean all

# Setting up the environment using root account
USER root

RUN touch /var/log/forked-daapd.log && \
    chown ubuntu.root /var/log/forked-daapd.log

RUN touch /var/run/forked-daapd.pid && \
    chown ubuntu.root /var/run/forked-daapd.pid

RUN update-rc.d avahi-daemon defaults

RUN mkdir /usr/share/forked-daapd/ && \
    cp -R $WORKDIR/forked-daapd/htdocs /usr/share/forked-daapd/htdocs

RUN ln -s $WORKDIR/MP3 /tmp/MP3

#The script needs to launch dbus and avahi-daemon using sudo
RUN echo "ALL ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Switch back to ubuntu account
USER ubuntu
RUN mkdir ${WORKDIR}/db

# Download the scripts to process results
RUN git clone https://${USR}:${PSW}@github.com/Alan32Liu/diff-gcov.git && \
    cp "/home/ubuntu/diff-gcov/gcovr-new.py" "${WORKDIR}/LightFTP-gcov/Source/Release/" && \
    cp "/home/ubuntu/diff-gcov/process_gcovr_reports.py" "${WORKDIR}/LightFTP-gcov/Source/Release/"
