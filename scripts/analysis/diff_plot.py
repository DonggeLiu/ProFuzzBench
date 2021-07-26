#!/usr/bin/env python3

import pdb
import argparse
from pandas import read_csv
from pandas import DataFrame
from pandas import Grouper
from matplotlib import pyplot as plt
import pandas as pd

FUZZERS = ['AFLNet', 'AFLNet_Legion']


# FUZZERS = ['AFLNet_Legion']


def main(csv_file, put, runs, cut_off, step, out_file,
         message, legion_version, profuzzbench_version, profuzzbench_clean, excluded_fuzzer, excluded_run):

    excluded_fuzzer = excluded_fuzzer if excluded_fuzzer else []
    excluded_run = excluded_run if excluded_run else []
    excluded_pairs = list(zip(excluded_fuzzer, excluded_run))

    # Read the results
    df = read_csv(csv_file)

    # Calculate the mean of code coverage
    # Store in a list first for efficiency
    mean_list = []
    each_list = []
    max_list = []
    min_list = []
    median_list = []

    for subject in [put]:
        for fuzzer in FUZZERS:
            fuzzer = fuzzer.lower()
            for cov_type in ['b_abs', 'b_per', 'l_abs', 'l_per']:
                # get subject & fuzzer & cov_type-specific dataframe
                df1 = df[(df['subject'] == subject) &
                         (df['fuzzer'] == fuzzer) &
                         (df['cov_type'] == cov_type)]

                mean_list.append((subject, fuzzer, cov_type, 0, 0.0))
                for run in range(1, runs + 1, 1):
                    if (fuzzer, str(run)) in excluded_pairs:
                        continue
                    each_list.append((subject, "{}_{}".format(fuzzer, run), cov_type, 0, 0.0))

                for time in range(1, cut_off + 1, step):
                    cov_total = 0
                    run_count = 0
                    cov_list = []

                    for run in range(1, runs + 1, 1):
                        if (fuzzer, str(run)) in excluded_pairs:
                            continue
                        cov_each = 0
                        # get run-specific data frame
                        df2 = df1[df1['run'] == run]

                        # get the starting time for this run
                        start = df2.iloc[0, 0]

                        # get all rows given a cutoff time
                        df3 = df2[df2['time'] <= start + time * 60]

                        # update total coverage and #runs
                        cov_total += df3.tail(1).iloc[0, 5]
                        cov_list.append(df3.tail(1).iloc[0, 5])

                        each_list.append((subject, "{}_{}".format(fuzzer, run), cov_type, time, df3.tail(1).iloc[0, 5]))

                        run_count += 1

                    # add a new row
                    mean_list.append((subject, fuzzer, cov_type, time, cov_total / run_count))
                    max_list.append((subject, fuzzer, cov_type, time, max(cov_list)))
                    min_list.append((subject, fuzzer, cov_type, time, min(cov_list)))
                    median_list.append((subject, fuzzer, cov_type, time, sorted(cov_list)[run_count//2]))

    # Convert the list to a dataframe
    mean_df = pd.DataFrame(mean_list, columns=['subject', 'fuzzer', 'cov_type', 'time', 'cov'])
    each_df = pd.DataFrame(each_list, columns=['subject', 'fuzzer', 'cov_type', 'time', 'cov'])
    max_df = pd.DataFrame(max_list, columns=['subject', 'fuzzer', 'cov_type', 'time', 'cov'])
    min_df = pd.DataFrame(min_list, columns=['subject', 'fuzzer', 'cov_type', 'time', 'cov'])
    median_df = pd.DataFrame(median_list, columns=['subject', 'fuzzer', 'cov_type', 'time', 'cov'])

    auc_df = pd.DataFrame(columns=['subject', 'cov_type', 'time', 'diff'])
    for key, category in mean_df.groupby(['subject', 'cov_type']):
        prev_cov = 0;
        prev_i = len(auc_df);
        for i, item in enumerate(category.groupby(['time'])):
            #pdb.set_trace()
            time, grp = item
            #auc_df.loc[prev_i+i] = [key[0], key[1], time, grp[grp['fuzzer']=='aflnet_legion']['cov'].item() - grp[grp['fuzzer']=='aflnet']['cov'].item() + prev_cov]
            auc_df.loc[prev_i+i] = [key[0], key[1], time, grp[grp['fuzzer']=='aflnet_legion']['cov'].item() - grp[grp['fuzzer']=='aflnet']['cov'].item()]
            prev_cov = auc_df.loc[i]['diff'].item() 
            # auc_df['subject']['cov_type']['time'] = previous time + new diff 

    fig, axes = plt.subplots(2, 2, figsize=(20, 10))
    title = "Code coverage analysis: {}\n{}\n{}\n{}\n{}".format(
        subject, message, legion_version[:-1], profuzzbench_version, profuzzbench_clean)
    fig.suptitle(title)

    for data_frame in [auc_df]:
        legends = [[], [], [], []]
        alpha = 0.2 if data_frame is each_df else 1
        if data_frame is max_df or data_frame is min_df:
            line_style = ':'
        elif data_frame is median_df:
            line_style = '--'
        else:
            line_style = '-'
        for key, grp in data_frame.groupby(['cov_type']):
            colour = 'C3'
            #pdb.set_trace()
            if key == 'b_abs':
                axes[0, 0].plot(grp['time'],
                                grp['diff'],
                                color=colour,
                                alpha=alpha,
                                linestyle=line_style)
                legends[0].append('AUC (legion-aflnet)')
                # axes[0, 0].set_title('Edge coverage over time (#edges)')
                axes[0, 0].set_xlabel('Time (in min)')
                axes[0, 0].set_ylabel('edges AUC (legion-aflnet)')
            if key == 'b_per':
                axes[1, 0].plot(grp['time'],
                                grp['diff'],
                                color=colour,
                                alpha=alpha,
                                linestyle=line_style)
                legends[1].append('AUC (legion-aflnet)')
                # axes[1, 0].set_title('Edge coverage over time (%)')
                axes[1, 0].set_xlabel('Time (in min)')
                axes[1, 0].set_ylabel('Edge coverage (%)')
            if key == 'l_abs':
                axes[0, 1].plot(grp['time'],
                                grp['diff'],
                                color=colour,
                                alpha=alpha,
                                linestyle=line_style)
                legends[2].append('AUC (legion-aflnet)')
                # axes[0, 1].set_title('Line coverage over time (#lines)')
                axes[0, 1].set_xlabel('Time (in min)')
                axes[0, 1].set_ylabel('#lines')
            if key == 'l_per':
                axes[1, 1].plot(grp['time'],
                                grp['diff'],
                                color=colour,
                                alpha=alpha,
                                linestyle=line_style)
                legends[3].append('AUC (legion-aflnet)')
                # axes[1, 1].set_title('Line coverage over time (%)')
                axes[1, 1].set_xlabel('Time (in min)')
                axes[1, 1].set_ylabel('Line coverage (%)')

        for i in range(0, 2):
            for j in range(0, 2):
                axes[j, i].legend(tuple(legends[2 * i + j]), loc='best')
                axes[j, i].grid()

    # Save to file
    plt.savefig(out_file)


# Parse the input arguments
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--csv_file', type=str, required=True, help="Full path to results.csv")
    parser.add_argument('-p', '--put', type=str, required=True, help="Name of the subject program")
    parser.add_argument('-r', '--runs', type=int, required=True, help="Number of runs in the experiment")
    parser.add_argument('-c', '--cut_off', type=int, required=True, help="Cut-off time in minutes")
    parser.add_argument('-s', '--step', type=int, required=True, help="Time step in minutes")
    parser.add_argument('-o', '--out_file', type=str, required=True, help="Output file")
    parser.add_argument('-m', '--message', type=str, required=True, help="the hyper-parameter setting")
    parser.add_argument('-lv', '--legion_version', type=str, required=True, help="the version of AFLNet_Legion")
    parser.add_argument('-pv', '--profuzzbench_version', type=str, required=True, help="the version of ProFuzzBench")
    parser.add_argument('-pc', '--profuzzbench_clean', type=str, required=True, help="If ProFuzzBench is clean")
    parser.add_argument('-ef', '--exclude_fuzzer', action='append', required=False, help="Exclude fuzzers")
    parser.add_argument('-er', '--exclude_run', action='append', required=False, help="Exclude runs")
    args = parser.parse_args()
    main(args.csv_file, args.put, args.runs, args.cut_off, args.step, args.out_file,
         args.message, args.legion_version, args.profuzzbench_version, args.profuzzbench_clean, args.exclude_fuzzer, args.exclude_run)
