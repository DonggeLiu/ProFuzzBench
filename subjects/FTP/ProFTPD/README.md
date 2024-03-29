Please carefully read the [main README.md](../../../README.md), which is stored in the benchmark's root folder, before following this subject-specific guideline.

# Fuzzing ProFTPD server with AFLNet and AFLnwe
Please follow the steps below to run and collect experimental results for ProFTPD, which is a popular File Transfer Protocol (FTP) server.

## Step-1. Build a docker image
The following commands create a docker image tagged ProFTPD. The image should have everything available for fuzzing and code coverage calculation.

```bash
cd $PFBENCH
cd subjects/FTP/ProFTPD
docker build --no-cache --rm -t proftpd --build-arg USR=<username> --build-arg PSW=<password> .
```

## Step-2. Run fuzzing
The following commands run 4 instances of AFLNet and 4 instances of AFLnwe to simultaenously fuzz ProFTPD in 60 minutes.

```bash
cd $PFBENCH
mkdir results-proftpd

profuzzbench_exec_common.sh proftpd 4 results-proftpd aflnet out-proftpd-aflnet "-t 1000+ -m none -P FTP -D 10000 -q 3 -s 3 -E -K -c clean" 3600 5 &
profuzzbench_exec_common.sh proftpd 4 results-proftpd aflnwe out-proftpd-aflnwe "-t 1000+ -m none -D 10000 -K -c clean" 3600 5
```

## Step-3. Collect the results
The following commands collect the  code coverage results produced by AFLNet and AFLnwe and save them to results.csv.

```bash
cd $PFBENCH/results-proftpd

profuzzbench_generate_csv.sh proftpd 4 aflnet results.csv 0
profuzzbench_generate_csv.sh proftpd 4 aflnwe results.csv 1
```

## Step-4. Analyze the results
The results collected in step 3 (i.e., results.csv) can be used for plotting. Use the following command to plot the coverage over time and save it to a file.

```
cd $PFBENCH/results-proftpd

profuzzbench_plot.py -i results.csv -p proftpd -r 4 -c 60 -s 1 -o cov_over_time.png
```
