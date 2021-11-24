# One command to run them all

After:
1. Building the docker image of a benchmark subject (e.g. the [README.md](https://github.com/Alan32Liu/ProFuzzBench/tree/temp/subjects/FTP/LightFTP) of `lightftp` ), 
2. Creating a `Record` directory in the root of this repo (i.e. `/../ProFuzzBench/Record/`)

The script `run_all` allows us to automatically run experiments with that subject, collect experiement results, and analyse results in one command.

## Command
### tl;dr

The command for a typical experiment looks like:

```bash
run_all 0 x 1440 0 1 1 0.0025 1 1 3 3 lightftp
```

where the parameters are explained as follows.

### Parameters

The command `run_all` takes 12 **command-line parameters** in the following order:
1. The first parameter determines which fuzzer(s) to run:
    * 0: Both `AFLNet` and `AFLNetLegion`; 
    * 1: Just `AFLNetLegion`
2. If and only if the previous parameter is `1` (i.e. `AFLNetLegion` only), then use this parameter to input the directory to an existing result of `AFLNet`, this is necessary for result analysis.
3. Timeout (in minutes)
4. Log level, from `0` (log everthing) to `5` (log nothing)
5. Ignore assertions (ignore assertion errors in `AFLNetLegion`)
6. Let `AFLNetLegion` fuzz the `M3` regions of request sequence (see `AFLNet` paper for more detail):
    * `0`: do not fuzz `M3`
    * `1`: fuzz `M3`
7. `Rho`: the exploration ratio (see `Legion` paper for more detail)
8. Node selection algorithm of `AFLNetLegion`:
    * `0`: Random selection
    * `1`: UCT
9. Seed selection algorithm of `AFLNetLegion`:
    * `0`: Random selection
    * `1`: UCT
10. Node selection algorithm of `AFLNet`:
    * `1`: Random selection
    * `2`: Round-Robin
    * `3`: Favour
11. Seed selection algorithm of `AFLNet`:
    * `1`: Random selection
    * `2`: Round-Robin
    * `3`: Favour
12. Subject: the docker image name of the benchmark subject.

It also has two **in-script parameters**:
1. Tree Depth in the log of `AFLNetLegion`
2. Number of trials to run in this experiment

