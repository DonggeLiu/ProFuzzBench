#!/usr/bin/env python3

import pdb
import argparse
import pandas as pd
import numpy as np
import scipy.stats as st
from time import time
import math

from pandas import read_csv
from pandas import DataFrame
from pandas import Grouper
from matplotlib import pyplot as plt
# import matplotlib.ticker as mtick
import matplotlib.ticker as tick



# FUZZERS = ['AFLNet_FF', 'AFLNetLegion_UU', ]
plt.rcParams.update({'font.size': 18})

np.seterr(all='raise')
# FUZZERS = ['AFLNet_Legion']
# COLOURS = {
#     "AFLNet_RR":       ("C0", "dotted"),
#     "AFLNet_BB":       ("C0", "dashed"),
#     "AFLNet_FF":       ("C0", "solid"),
#     "AFLNetLegion_RR": ("C3", "dotted"),
#     "AFLNetLegion_UR": ("C3", "dashed"),
#     "AFLNetLegion_UU": ("C3", "solid")
# }

COLOURS = {
    "AFLNet_RR":       ("#74add1", "solid"),
    "AFLNet_BB":       ("#4575b4", "solid"),
    "AFLNet_FF":       ("#313695", "solid"),
    "AFLNetLegion_RR": ("#f46d43", "solid"),
    "AFLNetLegion_UR": ("#d73027", "solid"),
    "AFLNetLegion_UU": ("#a50026", "solid"),
}

FUZZER_ORDER = {
    "AFLNet_RR": 1,
    "AFLNet_BB": 2,
    "AFLNet_FF": 3,
    "AFLNetLegion_RR": 4,
    "AFLNetLegion_UR": 5,
    "AFLNetLegion_UU": 6,
}


def main(csv_files, put, runs, cut_off, step,
         # out_file,
         # message, legion_version, profuzzbench_version, profuzzbench_clean,
         excluded_fuzzer, excluded_run, suffix):

    excluded_fuzzer = excluded_fuzzer if excluded_fuzzer else []
    excluded_run = excluded_run if excluded_run else []
    excluded_pairs = list(zip(excluded_fuzzer, excluded_run))

    # Read the results
    # dfs = [read_csv(csv_file) for csv_file in csv_files]
    df = read_csv(csv_files)

    # Calculate the mean of code coverage
    # Store in a list first for efficiency
    mean_list = []
    each_list = []
    max_list = []
    min_list = []
    median_list = []
    ci_list = []
    # ci_low_list = []
    # ci_high_list = []

    for subject in [put]:
        for f_index, fuzzer in enumerate(FUZZERS):
            # fuzzer = fuzzer.lower()
            print(fuzzer)
            for cov_type in ['b_abs', 'b_per', 'l_abs', 'l_per']:
                    # get subject & fuzzer & cov_type-specific dataframe
                    df1 = df[(df['subject'] == subject) &
                             (df['fuzzer'] == fuzzer) &
                             (df['cov_type'] == cov_type)]

                    mean_list.append((subject, fuzzer, cov_type, 0, 0.0))
                    max_list.append((subject, fuzzer, cov_type, 0, 0.0))
                    min_list.append((subject, fuzzer, cov_type, 0, 0.0))
                    median_list.append((subject, fuzzer, cov_type, 0, 0.0))
                    ci_list.append((subject, fuzzer, cov_type, 0, (0.0, 0.0)))
                    # ci_low_list.append((subject, fuzzer, cov_type, 0, 0.0))
                    # ci_high_list.append((subject, fuzzer, cov_type, 0, 0.0))
                    for run in range(1, runs[f_index] + 1, 1):
                        if (fuzzer, str(run)) in excluded_pairs:
                            continue
                        each_list.append((subject, "{}_{}".format(fuzzer, run), cov_type, 0, 0.0))

                    for time in range(1, cut_off + 1, step):
                        cov_total = 0
                        run_count = 0
                        cov_list = []

                        for run in range(1, runs[f_index] + 1, 1):
                            if (fuzzer, str(run)) in excluded_pairs:
                                continue
                            cov_each = 0
                            # get run-specific data frame
                            df2 = df1[df1['run'] == run]

                            # get the starting time for this run
                            try:
                                start = df2.iloc[0, 0]
                            except:
                                pdb.set_trace()

                            # get all rows given a cutoff time
                            df3 = df2[df2['time'] <= start + time * 60]

                            # update total coverage and #runs
                            cov_total += df3.tail(1).iloc[0, 5]
                            cov_list.append(df3.tail(1).iloc[0, 5])

                            each_list.append((subject, "{}_{}".format(fuzzer, run), cov_type, time, df3.tail(1).iloc[0, 5]))

                            run_count += 1

                        # add a new row
                        try:
                            mean_list.append((subject, fuzzer, cov_type, time, cov_total / run_count))
                            # max_list.append((subject, fuzzer, cov_type, time, max(cov_list)))
                            # min_list.append((subject, fuzzer, cov_type, time, min(cov_list)))
                            # median_list.append((subject, fuzzer, cov_type, time, sorted(cov_list)[run_count//2]))

                            ci = st.t.interval(0.95, len(cov_list)-1, loc=np.mean(cov_list), scale=st.sem(cov_list)) \
                                if st.sem(cov_list) else \
                                [np.mean(cov_list), np.mean(cov_list)]
                        except:
                            pdb.set_trace()
                        ci_list.append((subject, fuzzer, cov_type, time, ci))
                        # ci_low_list.append(np.mean(cov_list) - ci)
                        # ci_high_list.append(np.mean(cov_list) + ci)

    # Convert the list to a dataframe
    mean_df = pd.DataFrame(mean_list, columns=['subject', 'fuzzer', 'cov_type', 'time', 'cov'])
    each_df = pd.DataFrame(each_list, columns=['subject', 'fuzzer', 'cov_type', 'time', 'cov'])
    max_df = pd.DataFrame(max_list, columns=['subject', 'fuzzer', 'cov_type', 'time', 'cov'])
    min_df = pd.DataFrame(min_list, columns=['subject', 'fuzzer', 'cov_type', 'time', 'cov'])
    median_df = pd.DataFrame(median_list, columns=['subject', 'fuzzer', 'cov_type', 'time', 'cov'])
    ci_df = pd.DataFrame(ci_list, columns=['subject', 'fuzzer', 'cov_type', 'time', 'cov'])
    # ci_low_df = pd.DataFrame(ci_low_list, columns=['subject', 'fuzzer', 'cov_type', 'time', 'cov'])
    # ci_high_df = pd.DataFrame(ci_high_list, columns=['subject', 'fuzzer', 'cov_type', 'time', 'cov'])

    bfig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    baxes = [ax1,
             ax2
             ]

    lfig, ax3 = plt.subplots()
    ax4 = ax3.twinx()
    laxes = [ax3,
             ax4
             ]

    # title = "Code coverage analysis: {}\n{}\n{}\n{}\n{}".format(
    #     subject,
    #     # message, legion_version[:-1], profuzzbench_version, profuzzbench_clean
    # )
    # fig.suptitle(title)
    # for data_frame in [ci_df, mean_df]:
    for data_frame in [ci_df, mean_df]:
        legends = [[], [], [], []]
        alpha = 0.2 if data_frame is each_df else 1
        if data_frame is max_df or data_frame is min_df:
            line_style = ':'
        elif data_frame is median_df:
            line_style = '--'
        else:
            line_style = '-'
        for key, grp in data_frame.groupby(['fuzzer', 'cov_type']):
            colour, line_style = COLOURS.get(key[0], ("black", (0, (1, 10))))
            alpha = 0.2
            if key[1] == 'b_abs':
                if data_frame is ci_df:
                    low = [ci[0] for ci in grp['cov']]
                    high = [ci[1] for ci in grp['cov']]
                    # baxes[0].fill_between(grp['time'], low, high,
                    #                         color=colour, alpha=alpha)
                    baxes[0].plot(
                        grp['time'],
                        low,
                        color=colour,
                        linestyle='dotted',
                        # label=key[0],
                    )
                    baxes[0].plot(
                        grp['time'],
                        high,
                        color=colour,
                        linestyle='dotted',
                        # label=key[0],
                    )
                else:
                    baxes[0].plot(
                        # grp['cov'],
                        grp['time'],
                        grp['cov'],
                        color=colour,
                        linestyle=line_style,
                        label=key[0],
                    )
                legends[0].append(key[0])
                # axes[0, 0].set_title('Edge coverage over time (#edges)')
                baxes[0].set_xlabel('Time (minute)')
                baxes[0].set_ylabel('Number of edges covered')

            if key[1] == 'b_per':
                if data_frame is ci_df:
                    # pdb.set_trace()
                    low = [ci[0] for ci in grp['cov']]
                    high = [ci[1] for ci in grp['cov']]
                    # baxes[1].fill_between(grp['time'], low, high,
                    #                         color=colour, alpha=alpha)
                else:
                    baxes[1].plot(
                        grp['time'],
                        grp['cov'],
                        color=colour,
                        linestyle=line_style,
                        # label=key[0],
                    )
                # legends[1].append(key[0])
                # axes[1, 0].set_ylim([0, 100])
                baxes[1].set_xlabel('Time (minute)')
                # baxes[1].set_ylabel('Percentage of edges covered (%)')

            if key[1] == 'l_abs':
                if data_frame is ci_df:
                    # pdb.set_trace()
                    low = [ci[0] for ci in grp['cov']]
                    high = [ci[1] for ci in grp['cov']]
                    # laxes[0].fill_between(grp['time'], low, high,
                    #                         color=colour, alpha=alpha)
                    laxes[0].plot(
                        grp['time'],
                        low,
                        color=colour,
                        linestyle='dotted',
                        # label=key[0],
                    )
                    laxes[0].plot(
                        grp['time'],
                        high,
                        color=colour,
                        linestyle='dotted',
                        # label=key[0],
                    )
                else:
                    laxes[0].plot(
                        # grp['cov'],
                        grp['time'],
                        grp['cov'],
                        color=colour,
                        linestyle=line_style,
                        label=key[0],
                    )
                legends[2].append(key[0])
                # axes[0, 0].set_title('Edge coverage over time (#edges)')
                laxes[0].set_xlabel('Time (minute)')
                laxes[0].set_ylabel('Number of lines covered')

            if key[1] == 'l_per':
                if data_frame is ci_df:
                    # pdb.set_trace()
                    low = [ci[0] for ci in grp['cov']]
                    high = [ci[1] for ci in grp['cov']]
                    # laxes[1].fill_between(grp['time'], low, high,
                    #                         color=colour, alpha=alpha)
                else:
                    laxes[1].plot(grp['time'],
                                    grp['cov'],
                                    color=colour,
                                    linestyle=line_style)
                legends[3].append(key[0])
                # axes[1, 1].set_ylim([0, 100])
                laxes[1].set_xlabel('Time (minute)')
                # laxes[1].set_ylabel('Percentage of lines covered (%)')

    for j in [0]:
        handles, labels = baxes[j].get_legend_handles_labels()
        # sort both labels and handles by labels
        labels, handles = zip(*sorted(zip(labels, handles), key=lambda f: FUZZER_ORDER[f[0]]))
        baxes[j].legend(handles, labels)

        handles, labels = laxes[j].get_legend_handles_labels()
        # sort both labels and handles by labels
        labels, handles = zip(*sorted(zip(labels, handles), key=lambda f: FUZZER_ORDER[f[0]]))
        laxes[j].legend(handles, labels)

    # for j in range(0, 1):
    #     pdb.set_trace()
    #     baxes[j].legend(sorted(legends[j], key=lambda v: FUZZER_ORDER[v]), loc='best')
    #     baxes[j].grid()
    #     laxes[j].legend(sorted(legends[2+j], key=lambda v: FUZZER_ORDER[v]), loc='best')
    #     baxes[j].grid()

    # exp = lambda x: 10 ** x
    # log = lambda x: np.log(x)
    # baxes[0].set_yscale('function', functions=(exp, log))
    # baxes[1].set_yscale('function', functions=(exp, log))
    # laxes[0].set_yscale('function', functions=(exp, log))
    # laxes[1].set_yscale('function', functions=(exp, log))

    # def exp(x):
    #     try:
    #         v = 10 ** (x/1000)
    #     except Exception as e:
    #         print(e)
    #         pdb.set_trace()
    #     return v
    #
    # def exp2(x):
    #     try:
    #         v = 10 ** (x*27543/100/1000)
    #     except Exception as e:
    #         print(e)
    #         pdb.set_trace()
    #     return v
    #
    # def exp3(x):
    #     try:
    #         v = 10 ** (x*30053/100/1000)
    #     except Exception as e:
    #         print(e)
    #         pdb.set_trace()
    #     return v
    #
    # def log(x):
    #     try:
    #         # v = np.log(x/1000)
    #         v = x
    #     except Exception as e:
    #         print(e)
    #         pdb.set_trace()
    #     return v

    # baxes[0].set_ylim([0, 3200])
    # baxes[1].set_ylim([0, 3200/27543 * 100])
    # laxes[0].set_ylim([0, 5200])
    # laxes[1].set_ylim([0, 5200/30053 * 100])

    # baxes[0].set_ylim([1, 10000])
    # laxes[0].set_ylim([1, 10000])
    # baxes[0].set_yscale('log')
    # laxes[0].set_yscale('log')
    # baxes[0].set_yscale('function', functions=(exp, log))
    # baxes[1].set_yscale('function', functions=(exp2, log))
    # laxes[0].set_yscale('function', functions=(exp, log))
    # laxes[1].set_yscale('function', functions=(exp3, log))

    # # baxes[0].set_yticks(ticks=[0, 10, 100, 1000, 10000], minor=False)
    # bys = [0, 2000, 2500, 2750, 3000, 3200]
    # lys = [0, 4000, 4500, 4750, 5000, 5200]
    # baxes[0].set_yticks(ticks=bys, minor=False)
    # pdb.set_trace()
    # baxes[1].set_yticks(ticks=[y/27543 * 100 for y in baxes[0].yaxis.get_majorticklabels()], minor=False)
    # laxes[0].set_yticks(ticks=lys, minor=False)
    # laxes[1].set_yticks(ticks=[y/30053 * 100 for y in laxes[0].get_yticklabels()], minor=False)

    def y_fmt(x, y):
        return "{:.3}%".format(x)

    baxes[1].yaxis.set_major_formatter(tick.FuncFormatter(y_fmt))
    laxes[1].yaxis.set_major_formatter(tick.FuncFormatter(y_fmt))

    # baxes[0].set_xscale('log')
    # laxes[0].set_xscale('log')
    # baxes[0].set_xlim([1, 10000])
    # laxes[0].set_xlim([1, 10000])

    # baxes[0].set_yscale('log')
    # baxes[1].set_yscale('log')
    # laxes[0].set_yscale('log')
    # laxes[1].set_yscale('log')
    # baxes[0].set_ylim(bottom=0.01)
    # baxes[1].set_ylim(bottom=0.01)
    # laxes[0].set_ylim(bottom=0.01)
    # laxes[1].set_ylim(bottom=0.01)

    # baxes[0].set_ylim(bottom=4000)
    # baxes[1].set_ylim(bottom=17.019103944)
    # laxes[0].set_ylim(bottom=8000)
    # laxes[1].set_ylim(bottom=21.475933532)

    # Save to file
    # bfig.set_size_inches(12, 6)
    # lfig.set_size_inches(12, 6)

    # bfig.savefig(subject + "_bfig_{}.pdf".format(suffix), bbox_inches="tight")
    # lfig.savefig(subject + "_lfig_{}.pdf".format(suffix), bbox_inches="tight")
    # bfig.savefig(subject + "_bfig_{}.png".format(suffix), bbox_inches="tight")
    # lfig.savefig(subject + "_lfig_{}.png".format(suffix), bbox_inches="tight")

    bfig.savefig("b_{}.pdf".format(suffix), bbox_inches="tight")
    lfig.savefig("l_{}.pdf".format(suffix), bbox_inches="tight")
    bfig.savefig("b_{}.png".format(suffix), bbox_inches="tight")
    lfig.savefig("l_{}.png".format(suffix), bbox_inches="tight")


    #pdb.set_trace()
    plt.plot()
    plt.show()
    # bfig.plot()
    # lfig.plot()
    # bfig.show()
    # lfig.show()

# Parse the input arguments
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--csv_file', type=str, required=True, help="Full path to results.csv")
    parser.add_argument('-p', '--put', type=str, required=True, help="Name of the subject program")
    parser.add_argument('-f', '--fuzzers', action='append', required=True)
    parser.add_argument('-r', '--runs', action='append', type=int, required=True, help="Number of runs in the experiment")
    parser.add_argument('-c', '--cut_off', type=int, required=True, help="Cut-off time in minutes")
    parser.add_argument('-s', '--step', type=int, required=True, help="Time step in minutes")
    parser.add_argument('-x', '--suffix', type=str, required=False, help="Is it for AFLNet or AFLNetLegion or both?")
    # parser.add_argument('-o', '--out_file', type=str, required=True, help="Output file")
    # parser.add_argument('-m', '--message', type=str, required=True, help="the hyper-parameter setting")
    # parser.add_argument('-lv', '--legion_version', type=str, required=True, help="the version of AFLNet_Legion")
    # parser.add_argument('-pv', '--profuzzbench_version', type=str, required=True, help="the version of ProFuzzBench")
    # parser.add_argument('-pc', '--profuzzbench_clean', type=str, required=True, help="If ProFuzzBench is clean")

    parser.add_argument('-ef', '--exclude_fuzzer', action='append', required=False, help="Exclude fuzzers")
    parser.add_argument('-er', '--exclude_run', action='append', required=False, help="Exclude runs")
    args = parser.parse_args()
    FUZZERS = args.fuzzers

    for fuzzer, run in zip(args.fuzzers, args.runs):
        print(fuzzer, run)

    main(args.csv_file, args.put, args.runs, args.cut_off, args.step,
         # args.out_file,
         # args.message, args.legion_version, args.profuzzbench_version, args.profuzzbench_clean,
         args.exclude_fuzzer, args.exclude_run, args.suffix)


# TODO:
#   3. [ ] merge of all data (repetitions, selection algorithms) into one fig

