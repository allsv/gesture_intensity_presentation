# analysis.py
# Paweł Szczepański
# 2020-06-15
# analysing elan files

import os
import re
import numpy as np
from numpy import mean
import matplotlib.pyplot as plt
from math import sqrt
from scipy.stats import sem
from scipy.stats import t

def list_tiers():
    # list all .eaf files in the source directory
    directory = os.path.join(".", "elan_files")
    filelist = os.listdir(directory)
    eaf_filenames = [filename for filename in filelist
                     if re.search(r'.+\.eaf$', filename)]
    print(eaf_filenames)

    # append the name of tier and number of gestures in tier to a shared list
    all_tiers = []
    for eaf_file in eaf_filenames:
        all_tiers.append(file_tiers(eaf_file))
    return all_tiers


def file_tiers(filename):
    # open file and read lines from file
    last_name = re.sub(r".eaf", r"", filename)
    input_file = open(os.path.join(".", "elan_files", filename),
                      encoding="utf-8")
    input_lines = input_file.readlines()
    input_file.close()

    # create a dictionary with tiers and number of gestures on a tier
    tiers = {}
    for ln in input_lines:
        if ln.startswith("    <TIER"):
            tier_type = re.sub(
                r'    <TIER LINGUISTIC_TYPE_REF="default-lt" TIER_ID="',
                r'',
                re.sub(r'">\n', r'', re.sub(r'/', r'', ln))
                )
            tiers[last_name + "_" + tier_type] = count_gestures(
                                                        input_lines,
                                                        tier_type
                                                        )
    return tiers


def count_gestures(lines, type):
    lines_copy = []
    encounter = '    <TIER LINGUISTIC_TYPE_REF="default-lt" TIER_ID="'\
                + type
    for ln in lines:
        lines_copy.append(ln)
    for i in range(len(lines)):
        if lines[i].startswith(encounter):
            break
        del lines_copy[0]
    for ln in lines_copy:
        print(ln)
    counter = 0
    for ln in lines_copy:
        if ln == "    </TIER>\n":
            break
        if ln.startswith("                <ANNOTATION_VALUE>"):
            counter += 1
        else:
            pass
    return counter


def plot_tiers():
    # data to plot
    all_tiers = list_tiers()
    gestures_abo = []
    gestures_sad = []
    last_names = []
    for file in all_tiers:
        for tier in file:
            last_name = re.sub(r'_...', r'', tier)
            tier_type = re.sub(r'.*_', r'', tier)
            if last_name not in last_names:
                last_names.append(last_name)
            if tier_type.startswith("ABO"):
                gestures_abo.append(file[tier])
            elif tier_type.startswith("SĄD"):
                gestures_sad.append(file[tier])
    n_groups = len(last_names)

    # test
    print(n_groups)
    print(last_names)
    print(gestures_abo)
    print(gestures_sad)

    # create bar chart
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.3
    opacity = 0.8

    plt.bar(index, gestures_abo, bar_width,
            label='Debata o aborcji', color=(0.5, 0.1, 0.1, opacity))
    plt.bar(index + bar_width, gestures_sad, bar_width,
            label='Debata o sądach', color=(0.4, 0.2, 0.7, opacity))

    plt.xlabel('Osoba')
    plt.ylabel('Liczba gestów')
    plt.title('Liczba gestów w debacie wg osoby')
    plt.xticks(index + bar_width, last_names)
    plt.legend()

    plt.tight_layout()
    barchart_output_dir = os.path.join(".", "output_plots", "bar_chart.png")
    plt.savefig(barchart_output_dir)
    plt.show()

    # create means bar chart
    means = [mean(gestures_abo), mean(gestures_sad)]
    index = np.arange(len(means))
    fig, ax = plt.subplots()
    bar_width = 0.6
    opacity = 0.8

    plt.bar(index, means, bar_width,
            color=[(0.5, 0.1, 0.1, opacity), (0.4, 0.2, 0.7, opacity)])
    plt.xlabel('Debata')
    plt.ylabel('Średnia liczba gestów')
    plt.title('')
    plt.xticks(index, ("Debata o aborcji", "Debata o sądach"))

    # create t-test table
    t_stat, df, cv, p = independent_ttest(gestures_abo, gestures_sad, 0.05)
    print(t_stat, df, cv, p)
    t_test_values = [(str(t_stat), str(df), str(cv), str(p))]

    table_colums = ('t', 'df', 'cv', 'p')
    table_rows = [('value')]

    the_table = plt.table(cellText=t_test_values,
                          cellLoc='center',
                          rowLabels=table_rows,
                          colLabels=table_colums,
                          colWidths=[0.23 for x in table_colums],
                          loc='top')

    the_table.set_fontsize(16)
    the_table.scale(1.3, 1.3)

    plt.subplots_adjust(left=0.2, bottom=0.2)
    barchart_output_dir = os.path.join(".", "output_plots",
                                       "mean_bar_chart.png")
    plt.savefig(barchart_output_dir)
    plt.show()


def independent_ttest(data1, data2, alpha):
    # calculate means
    mean1, mean2 = mean(data1), mean(data2)
    # calculate standard errors
    se1, se2 = sem(data1), sem(data2)
    # standard error on the difference between the samples
    sed = sqrt(se1**2.0 + se2**2.0)
    # calculate the t statistic
    t_stat = (mean1 - mean2) / sed
    # degrees of freedom
    df = len(data1) + len(data2) - 2
    # calculate the critical value
    cv = t.ppf(1.0 - alpha, df)
    # calculate the p-value
    p = (1.0 - t.cdf(abs(t_stat), df)) * 2.0
    # return everything
    return t_stat, df, cv, p


plot_tiers()
