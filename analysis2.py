# analysis.py
# Paweł Szczepański
# 2020-06-15
# analysing elan files

import os
import re
import numpy as np
from numpy import mean
import matplotlib.pyplot as plt
# from math import sqrt
# from scipy.stats import sem
# from scipy.stats import t


def list_tiers():
    # list all .eaf files in the source directory
    directory = os.path.join(".", "elan_files_2")
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
    input_file = open(os.path.join(".", "elan_files_2", filename),
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
    a_counter = 0
    b_counter = 0
    m_counter = 0
    d_counter = 0
    for ln in lines_copy:
        if ln == "    </TIER>\n":
            break
        if ln.startswith("                <ANNOTATION_VALUE>beat"):
            a_counter += 1
            b_counter += 1
        if ln.startswith("                <ANNOTATION_VALUE>metaphoric"):
            a_counter += 1
            m_counter += 1
        if ln.startswith("                <ANNOTATION_VALUE>deictic"):
            a_counter += 1
            d_counter += 1
        else:
            pass
    return a_counter, b_counter, m_counter, d_counter


def print_charts():
    abo_beat = []
    abo_meta = []
    abo_deic = []

    sad_beat = []
    sad_meta = []
    sad_deic = []

    for file in list_tiers():
        for key in file:
            if key.endswith("ABO"):
                abo_beat.append(file[key][1])
                abo_meta.append(file[key][2])
                abo_deic.append(file[key][3])
            elif key.endswith("SĄD"):
                sad_beat.append(file[key][1])
                sad_meta.append(file[key][2])
                sad_deic.append(file[key][3])

    print(abo_beat, abo_meta, abo_deic)
    print(sad_beat, sad_meta, sad_deic)

    abo_means = [mean(abo_beat), mean(abo_meta), mean(abo_deic)]
    sad_means = [mean(sad_beat), mean(sad_meta), mean(sad_deic)]

    groups = ["uderzenia", "gesty metaforyczne", "gesty wskazujące"]
    n_groups = len(groups)

    # create bar chart
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.3
    opacity = 0.8

    plt.bar(index, abo_means, bar_width,
            label='Debata o aborcji', color=(0.5, 0.1, 0.1, opacity))
    plt.bar(index + bar_width, sad_means, bar_width,
            label='Debata o sądach', color=(0.4, 0.2, 0.7, opacity))

    plt.xlabel('Typ gestu')
    plt.ylabel('Średnia liczba gestów')
    plt.title('Średnia liczba gestów w debacie wg typu gestu')
    plt.xticks(index + bar_width/2, groups)
    plt.legend()

    plt.tight_layout()
    barchart_output_dir = os.path.join(".", "output_plots",
                                       "type_bar_chart.png")
    plt.savefig(barchart_output_dir)
    plt.show()


print_charts()
