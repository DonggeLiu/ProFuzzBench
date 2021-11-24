Please carefully read the [main README.md](../../../README.md), which is stored in the benchmark's root folder, before following this subject-specific guideline.

# Fuzzing LightFTP server with AFLNet and AFLNetLegion
Please follow the steps below to run and collect experimental results for LightFTP, which is a lightweight File Transfer Protocol (FTP) server.

## Step-1. Build a docker image
The following commands create a docker image tagged lightftp. The image should have everything available for fuzzing and code coverage calculation.

```bash
docker build --no-cache --force-rm -t lightftp .
```
Note that the `--no-cache` and `--force-rm` are not always necesary.
They are used here to ensure we always use the latest version of `AFLNet`, `AFLNetLegion`, etc.


## Step-2. Run experiments

See [README.md](https://github.com/Alan32Liu/ProFuzzBench/tree/temp/scripts) of `run_all`
