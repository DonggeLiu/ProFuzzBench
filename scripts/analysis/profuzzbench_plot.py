#!/usr/bin/env python3

import argparse
import pdb

from pandas import read_csv
from pandas import DataFrame
from pandas import Grouper
from matplotlib import pyplot as plt
from matplotlib.text import Text
import pandas as pd


FUZZERS = [['AFLNet', 'AFLNet_Legion'], ['AFLNet', 'AFLNet_Legion'], ['AFLNet', 'AFLNet_Legion'], ['AFLNet', 'AFLNet_Legion']]
#FUZZERS = ['AFLNet_Legion']


def main(csv_file, put, runs, cut_off, step, out_file, 
         message, legion_version, profuzzbench_version, profuzzbench_clean, excluded_fuzzer, excluded_run):

  excluded_fuzzer = excluded_fuzzer if excluded_fuzzer else []
  excluded_run = excluded_run if excluded_run else []
  excluded_pairs = list(zip(excluded_fuzzer, excluded_run))

  #Read the results
  df = read_csv(csv_file)

  #Calculate the mean of code coverage
  #Store in a list first for efficiency
  mean_list = []

  for subject in [put]:
    for fuzzer in FUZZERS[0]:
      fuzzer = fuzzer.lower()
      for cov_type in ['b_abs', 'b_per', 'l_abs', 'l_per']:
        #get subject & fuzzer & cov_type-specific dataframe
        df1 = df[(df['subject'] == subject) & 
                         (df['fuzzer'] == fuzzer) & 
                         (df['cov_type'] == cov_type)]

        mean_list.append((subject, fuzzer, cov_type, 0, 0.0))
        for time in range(1, cut_off + 1, step):
          cov_total = 0
          run_count = 0

          for run in range(1, runs + 1, 1):
            if (fuzzer, str(run)) in excluded_pairs:
              continue
            #get run-specific data frame
            df2 = df1[df1['run'] == run]

            #get the starting time for this run
            start = df2.iloc[0, 0]

            #get all rows given a cutoff time
            df3 = df2[df2['time'] <= start + time*60]
            
            #update total coverage and #runs
            cov_total += df3.tail(1).iloc[0, 5]
            run_count += 1
          
          #add a new row
          mean_list.append((subject, fuzzer, cov_type, time, cov_total / run_count))

  #Convert the list to a dataframe
  mean_df = pd.DataFrame(mean_list, columns = ['subject', 'fuzzer', 'cov_type', 'time', 'cov'])

  fig, axes = plt.subplots(2, 2, figsize = (20, 10))
  title="Code coverage analysis: {}\n{}\n{}".format(subject, message, legion_version[:-1])
  title = "Code coverage analysis: {}\n{}\n{}\n{}\n{}".format(
    subject, message, legion_version[:-1], profuzzbench_version, profuzzbench_clean)
  fig.suptitle(title)


  for key, grp in mean_df.groupby(['fuzzer', 'cov_type']):
    colour = 'C3' if 'legion' in key[0] else 'C0'
    if key[1] == 'b_abs':
      axes[0, 0].plot(grp['time'], grp['cov'], color=colour)
      #axes[0, 0].annotate(grp['cov'].tolist()[-1], xy=(cut_off, grp['cov'].tolist()[-1] + 300*(0 if 'legion' in key[0] else -1)), color=colour)
      if 'legion' in key[0]:
        FUZZERS[0][1] =  FUZZERS[0][1] + ": {:0.2f}".format(grp['cov'].tolist()[-1])
      else:
        FUZZERS[0][0] = FUZZERS[0][0] + " "*12 + ": {:0.2f}".format(grp['cov'].tolist()[-1])
      axes[0, 0].set_title('Edge coverage over time (#edges)')
      axes[0, 0].set_xlabel('Time (in min)')
      axes[0, 0].set_ylabel('#edges')
    if key[1] == 'b_per':
      axes[1, 0].plot(grp['time'], grp['cov'], color=colour)
      #axes[1, 0].annotate(grp['cov'].tolist()[-1], xy=(cut_off, grp['cov'].tolist()[-1] + 5*(1 if 'legion' in key[0] else -1)), color=colour)
      if 'legion' in key[0]:
        FUZZERS[2][1] = FUZZERS[2][1] + ": {:0.2f}".format(grp['cov'].tolist()[-1])
      else:
        FUZZERS[2][0] = FUZZERS[2][0] + " "*12 + ": {:0.2f}".format(grp['cov'].tolist()[-1])
      axes[1, 0].set_title('Edge coverage over time (%)')
      axes[1, 0].set_ylim([0,100])
      axes[1, 0].set_xlabel('Time (in min)')
      axes[1, 0].set_ylabel('Edge coverage (%)')
    if key[1] == 'l_abs':
      axes[0, 1].plot(grp['time'], grp['cov'], color=colour)
      #axes[0, 1].annotate(grp['cov'].tolist()[-1], xy=(cut_off, grp['cov'].tolist()[-1] + 300*(0 if 'legion' in key[0] else 0)), color=colour)
      if 'legion' in key[0]:
        FUZZERS[1][1] = FUZZERS[1][1] + ": {:0.2f}".format(grp['cov'].tolist()[-1])
      else:
        FUZZERS[1][0] = FUZZERS[1][0] + " "*12 + ": {:0.2f}".format(grp['cov'].tolist()[-1])
      axes[0, 1].set_title('Line coverage over time (#lines)')
      axes[0, 1].set_xlabel('Time (in min)')
      axes[0, 1].set_ylabel('#lines')
    if key[1] == 'l_per':
      axes[1, 1].plot(grp['time'], grp['cov'], color=colour)
      #axes[1, 1].annotate(grp['cov'].tolist()[-1], xy=(cut_off, grp['cov'].tolist()[-1] + 5*(1 if 'legion' in key[0] else -1)), color=colour)
      if 'legion' in key[0]:
        FUZZERS[3][1] = FUZZERS[3][1] + ": {:0.2f}".format(grp['cov'].tolist()[-1])
      else:
        FUZZERS[3][0] = FUZZERS[3][0] + " "*12 + ": {:0.2f}".format(grp['cov'].tolist()[-1])
      axes[1, 1].set_title('Line coverage over time (%)')
      axes[1, 1].set_ylim([0,100])
      axes[1, 1].set_xlabel('Time (in min)')
      axes[1, 1].set_ylabel('Line coverage (%)')

  for i, ax in enumerate(fig.axes):
    legend = ax.legend(tuple(FUZZERS[i]), loc='best')
    for t in legend.get_texts():
      t.set_color("C3" if "Legion" in t.get_text() else "C0")
    ax.grid()

  #Save to file
  plt.savefig(out_file)

# Parse the input arguments
if __name__ == '__main__':
    parser = argparse.ArgumentParser()    
    parser.add_argument('-i','--csv_file',type=str,required=True,help="Full path to results.csv")
    parser.add_argument('-p','--put',type=str,required=True,help="Name of the subject program")
    parser.add_argument('-r','--runs',type=int,required=True,help="Number of runs in the experiment")
    parser.add_argument('-c','--cut_off',type=int,required=True,help="Cut-off time in minutes")
    parser.add_argument('-s','--step',type=int,required=True,help="Time step in minutes")
    parser.add_argument('-o','--out_file',type=str,required=True,help="Output file")
    parser.add_argument('-m','--message',type=str,required=True,help="the hyper-parameter setting")
    parser.add_argument('-lv', '--legion_version', type=str, required=True, help="the version of AFLNet_Legion")
    parser.add_argument('-pv', '--profuzzbench_version', type=str, required=True, help="the version of ProFuzzBench")
    parser.add_argument('-pc', '--profuzzbench_clean', type=str, required=True, help="If ProFuzzBench is clean")
    parser.add_argument('-ef', '--exclude_fuzzer', action='append', required=False, help="Exclude fuzzers")
    parser.add_argument('-er', '--exclude_run', action='append', required=False, help="Exclude runs")
    args = parser.parse_args()
    main(args.csv_file, args.put, args.runs, args.cut_off, args.step, args.out_file,
         args.message, args.legion_version, args.profuzzbench_version, args.profuzzbench_clean, args.exclude_fuzzer, args.exclude_run)

