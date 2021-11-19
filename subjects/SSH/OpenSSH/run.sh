#!/bin/bash

FUZZER=$1     #fuzzer name (e.g., aflnet) -- this name must match the name of the fuzzer folder inside the Docker container
OUTDIR=$2     #name of the output folder
OPTIONS=$3    #all configured options -- to make it flexible, we only fix some options (e.g., -i, -o, -N) in this script
TIMEOUT=$4    #time for fuzzing
SKIPCOUNT=$5  #used for calculating cov over time. e.g., SKIPCOUNT=5 means we run gcovr after every 5 test cases

strstr() {
  [ "${1#*$2*}" = "$1" ] && return 1
  return 0
}

# store the options to a set, which will be fed to afl-fuzz later
PARAMS=()
for i in $OPTIONS; do PARAMS+=("$i"); done

mkdir -p "$WORKDIR/openssh/$OUTDIR/"

#Commands for afl-based fuzzers (e.g., aflnet, aflnwe)
if $(strstr $FUZZER "afl"); then
  #Step-1. Do Fuzzing
  #Move to fuzzing folder
  cd $WORKDIR/openssh
  timeout -k 0 $TIMEOUT /home/ubuntu/${FUZZER}/afl-fuzz -d -i ${WORKDIR}/in-ssh -x ${WORKDIR}/ssh.dict -o $OUTDIR -N tcp://127.0.0.1/22 $OPTIONS ./sshd -d -e -p 22 -r -f sshd_config 2>"$WORKDIR/openssh/$OUTDIR/fuzzing_error"
  wait 

  #Step-2. Collect code coverage over time
  #Move to gcov folder
  cd $WORKDIR/openssh-gcov

  #The last argument passed to cov_script should be 0 if the fuzzer is afl/nwe and it should be 1 if the fuzzer is based on aflnet
  #0: the test case is a concatenated message sequence -- there is no message boundary
  #1: the test case is a structured file keeping several request messages
  if [ $FUZZER = "aflnwe" ]; then
    cov_script ${WORKDIR}/openssh/${OUTDIR}/ 22 ${SKIPCOUNT} ${WORKDIR}/openssh/${OUTDIR}/cov_over_time.csv 0
  else
    cov_script ${WORKDIR}/openssh/${OUTDIR}/ 22 ${SKIPCOUNT} ${WORKDIR}/openssh/${OUTDIR}/cov_over_time.csv 1
  fi

  gcovr -r . --html --html-details -o index.html
  mkdir ${WORKDIR}/openssh/${OUTDIR}/cov_html/
  cp *.html ${WORKDIR}/openssh/${OUTDIR}/cov_html/

  cd "${WORKDIR}/openssh-gcov/" || exit
  TIME_NOW=$(date +"%Y-%m-%d-%H=%M=%S")
  mkdir "${TIME_NOW}"
  python gcovr-new.py -b -c -r .. > "${TIME_NOW}/gcovr_report-${FUZZER}.txt"
  cp "${TIME_NOW}/gcovr_report-${FUZZER}.txt" "${WORKDIR}/openssh/${OUTDIR}"
  # Rrun process_gcovr_reports.py outside the container

  #Step-3. Save the result to the ${WORKDIR} folder
  #Tar all results to a file
  cd ${WORKDIR}/openssh
  tar -zcvf ${WORKDIR}/${OUTDIR}.tar.gz ${OUTDIR}
fi
