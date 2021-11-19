#!/usr/bin/env python3
import argparse
import csv
import pdb


def parse_results():
    parser = argparse.ArgumentParser(
        description="Parse the args needed by merge_results.py to merge results of multiple experiments")
    parser.add_argument("-r", "--result", action='append')
    parser.add_argument("-i", "--instance", action='append', type=int)
    parser.add_argument("-a", "--algorithm", required=False)
    parser.add_argument('-et', '--excluded_trials', action='append', required=False, help="Exclude fuzzers")
    parser.add_argument('-ef', '--excluded_fuzzers', action='append', required=False, help="Exclude fuzzers")
    parser.add_argument("-er", "--excluded_runs", action='append', required=False, help="Exclude runs")

    args = parser.parse_args()
    print(args.result)
    return args.result, args.instance, args.algorithm, args.excluded_trials, args.excluded_fuzzers, args.excluded_runs


def merge_results():
    assert all([".csv" == result[-len(".csv"):] for result in results])
    with open("merged_results.csv", "w") as merged_result:
        merged_result_writer = csv.writer(merged_result)
        for index, result in enumerate(results):
            with open(result, "r") as individual_result:
                individual_result_reader = list(csv.reader(individual_result))
                if index == 0:
                    merged_result_writer.writerow(individual_result_reader[0])
                for line in individual_result_reader[1:]:
                    if (str(index+1), line[2], str(line[3])) in excluded_results:
                        # print([
                        #     line[0],
                        #     line[1],
                        #     ("AFLNetLegion_" + algorithm[:2] if "legion" in line[2] else "AFLNet_" + algorithm[2:]),
                        #     sum(instances[:index]) + int(line[3]),
                        #     line[4],
                        #     line[5]
                        # ])
                        continue
                    merged_result_writer.writerow([
                        line[0],
                        line[1],
                        ("AFLNetLegion_" + algorithm[:2] if "legion" in line[2] else "AFLNet_" + algorithm[2:])
                        if algorithm else
                        line[2],
                        (sum(instances[:index]) + int(line[3])),
                        line[4],
                        line[5]
                    ])
                # if index == 0:
                #     merged_result_writer.writerow(
                #         individual_result_reader[0]
                #     )
                # for line in individual_result_reader[1:]:
                #     merged_result_writer.writerow(
                #         [line[0], line[1], line[2], sum(instances[:index])+int(line[3]), line[4], line[5]]
                #     )


if __name__ == '__main__':
    results, instances, algorithm, excluded_trials, excluded_fuzzers, excluded_runs = parse_results()
    if excluded_trials and excluded_fuzzers and excluded_runs:
        excluded_results = list(zip(excluded_trials, excluded_fuzzers, excluded_runs))
        print([(fuzzer, int(trial)-1, run) for trial, fuzzer, run in excluded_results])
    else:
        excluded_results = []
    merge_results()
