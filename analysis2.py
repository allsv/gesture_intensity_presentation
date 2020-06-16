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


for file in list_tiers():
    for key in file:
        print(key)
        print("Wszystkie gesty:", file[key][0])
        print("Uderzenia:", file[key][1])
        print("Gesty metaforyczne:", file[key][2])
        print("Gesty wskazujące:", file[key][3])
        print("\n")
