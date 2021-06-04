#!/bin/bash

DOCIMAGE=$1   #name of the docker image
RUNS=$2       #number of runs
SAVETO=$3     #path to folder keeping the results

FUZZER=$4     #fuzzer name (e.g., aflnet) -- this name must match the name of the fuzzer folder inside the Docker container
OUTDIR=$5     #name of the output folder created inside the docker container
OPTIONS=$6    #all configured options for fuzzing
TIMEOUT=$7    #time for fuzzing
SKIPCOUNT=$8  #used for calculating coverage over time. e.g., SKIPCOUNT=5 means we run gcovr after every 5 test cases

# Make sure the result folder exists
mkdir -p "${SAVETO}"

echo "${FUZZER} will run for ${TIMEOUT} seconds with ${OPTIONS}"
#keep all container ids
container_ids=()

#create one container for each run
for i in $(seq 1 "$RUNS"); do
  mkdir -p "${SAVETO}/${FUZZER}-${i}/"
  id=$(docker run --cpus=1 -d -it "$DOCIMAGE" /bin/bash -c "run ${FUZZER} ${OUTDIR} ${OPTIONS} ${TIMEOUT} ${SKIPCOUNT}")
  LOG_PATH=$(docker exec "${id}" bash -c 'echo "$AFLNET_LEGION_LOG"')
  WORKDIR=$(docker exec "${id}" bash -c 'echo "$WORKDIR"')
  container_ids+=("${id::12}") #store only the first 12 characters of a container ID
done

#wait until all these dockers are stopped
echo "${FUZZER}: Fuzzing in progress ..."
echo "${FUZZER}: Waiting for the following containers to stop: ${container_ids[*]}"
docker wait "${container_ids[@]}" > /dev/null
wait

#collect the fuzzing results from the containers
echo "${FUZZER}: Collecting results and save them to ${SAVETO}"
index=1
for id in "${container_ids[@]}"; do
  echo "${FUZZER}: Collecting results from container ${id} to ${SAVETO}/${FUZZER}-${index}/"
  mkdir -p "${SAVETO}/${FUZZER}-${index}/gcovr_reports"
  docker cp "${id}:/home/ubuntu/experiments/${OUTDIR}.tar.gz" "${SAVETO}/${OUTDIR}_${index}.tar.gz"
  docker cp "${id}:${LOG_PATH}" "${SAVETO}/${FUZZER}-${index}/log_${FUZZER}_${index}.ansi"
  docker cp "${id}:${WORKDIR}/gcovr_report-${FUZZER}.txt" \
    "${SAVETO}/${FUZZER}-${index}/gcovr_reports/gcovr_report-${FUZZER}_${index}.txt"
  index=$((index+1))
done


printf "\n%s: I am done!" "${FUZZER}"

date
