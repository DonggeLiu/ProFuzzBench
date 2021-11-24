Please carefully read the [main README.md](../../../README.md), which is stored in the benchmark's root folder, before following this subject-specific guideline.

# Fuzzing Live555 server with AFLNet and AFLnwe
Please follow the steps below to run and collect experimental results for Live555.

## Step-1. Build a docker image
The following commands create a docker image tagged live555. The image should have everything available for fuzzing and code coverage calculation.

```bash
docker build --no-cache --force-rm -t live555 .
```
Note that the `--no-cache` and `--force-rm` are not always necesary.
They are used here to ensure we always use the latest version of `AFLNet`, `AFLNetLegion`, etc.


## Step-2. Run experiments

See [README.md](https://github.com/Alan32Liu/ProFuzzBench/tree/temp/scripts) of `run_all`
