#!/usr/bin/env python3
import argparse
import csv
import pdb


def parse_results():
    parser = argparse.ArgumentParser(
        description="Parse the args needed by merge_results.py to merge results of multiple experiments")
    parser.add_argument("-r", "--result", action='append')
    # parser.add_argument("-i", "--instance", action='append', type=int)
    # parser.add_argument("-a", "--algorithm", required=False)
    # parser.add_argument('-et', '--excluded_trials', action='append', required=False, help="Exclude fuzzers")
    # parser.add_argument('-ef', '--excluded_fuzzers', action='append', required=False, help="Exclude fuzzers")
    # parser.add_argument("-er", "--excluded_runs", action='append', required=False, help="Exclude runs")

    args = parser.parse_args()
    print(args.result)
    # return args.result, args.instance, args.algorithm, args.excluded_trials, args.excluded_fuzzers, args.excluded_runs
    return args.result


def merge_results():
    with open("new_test_merged_results.csv", "w") as new_result:
        new_result_writer = csv.writer(new_result)
        with open("test_merged_results.csv", "r") as old_result:
            old_result_reader = list(csv.reader(old_result))
            for line in old_result_reader:
                new_result_writer.writerow([
                    line[0],
                    line[1],
                    "aflnet_legion" if "Legion" in line[2] else "aflnet",
                    line[3],
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
    # result = parse_results()
    # results, instances, algorithm, excluded_trials, excluded_fuzzers, excluded_runs = parse_results()
    # excluded_results = list(zip(excluded_trials, excluded_fuzzers, excluded_runs))
    # print([(fuzzer, int(trial)-1, run) for trial, fuzzer, run in excluded_results])
    merge_results()
