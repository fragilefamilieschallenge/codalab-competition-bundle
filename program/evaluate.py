# -*- coding: utf-8 -*-
import sys
import os
import os.path
import csv
import pandas as pd
import numpy as np

# Setup for file locations
input_dir = sys.argv[1]
output_dir = sys.argv[2]

submit_dir = os.path.join(input_dir, 'res')
truth_dir = os.path.join(input_dir, 'ref')

if not os.path.isdir(submit_dir):
    raise ValueError("%s doesn't exist" % submit_dir)

elif not os.path.isdir(truth_dir):
    raise ValueError("%s doesn't exist" % truth_dir)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_filename = os.path.join(output_dir, 'scores.txt')
output_file = open(output_filename, 'wb')

gold = "truth.csv"
gold_file = os.path.join(truth_dir, gold)

submission = "prediction.csv"
corresponding_submission_file = os.path.join(submit_dir, submission)

s = [0, 0, 0, 0, 0, 0]
n = 0
if not os.path.exists(corresponding_submission_file):
    raise ValueError("Could not find submission file.")
if not os.path.exists(gold_file):
    raise ValueError("Could not find truth file.")

gold_df = pd.read_csv(gold_file, header=0)
submission_df = pd.read_csv(corresponding_submission_file, header=0)

# Check that submission directory contains a code file
has_code = False
for root, dirs, files in os.walk(input_dir):
    for fn in files:
        with open(root + '/' + fn, 'r') as f:
            assn_n = 0
            for line in f:
                assn_n += line.count('=') + line.count("<-")
                # NOTE: Consider stopping early if we find an assignment operation
                # NOTE: Also consider using the number of files in the submission to stop early
                # TODO: Confirm that this catches Stata
            if assn_n and fn != "narrative.txt":
                has_code = True
if not has_code:
    raise ValueError("Code file not found. If you think this error is incorrect, please email your submission to fragilefamilieschallenge@gmail.com and let us know.")

# Check that submission shape matches gold shape
gold_shape = gold_df.shape
submission_shape = submission_df.shape
if gold_shape != submission_shape:
    raise ValueError("Submission had incorrect size. Submission should have %d rows and %d columns, but had %d rows and %d columns." % (gold_shape[0], gold_shape[1], submission_shape[0], submission_shape[1]))

gold_df_sorted = gold_df.sort_values("challengeID")
submission_df_sorted = submission_df.sort_values("challengeID")

# Check that all idnums match
idnum_inequality = gold_df_sorted.challengeID != submission_df_sorted.challengeID
if (idnum_inequality.any()):
    raise ValueError("Submission had incorrect challengeID values.")

# Check that submission has no missing values
missing = submission_df_sorted.isnull()
any_missing = missing.any()
if (any_missing.any()):
    raise ValueError("Submission had missing values.")

# Set idnums as indexes and sort the rest of the columns alphabetically
gold_df_sorted = gold_df_sorted.set_index(["challengeID"])
gold_df_sorted = gold_df_sorted.sort_index(axis=1)
submission_df_sorted = submission_df_sorted.set_index(["challengeID"])
submission_df_sorted = submission_df_sorted.sort_index(axis=1)

# Compute squared error
sq_errors = (gold_df_sorted - submission_df_sorted)**2

# print("Differences are: ", diff)
l1 = 'GPA: ' + repr(round(np.nanmean(sq_errors.gpa), 5)) + '\n'
output_file.write(l1)
l2 = 'Grit:' + repr(round(np.nanmean(sq_errors.grit), 5)) + '\n'
output_file.write(l2)
l3 = 'Material_hardship:' + repr(round(np.nanmean(sq_errors.materialHardship), 5)) + '\n'
output_file.write(l3)
l4 = 'Eviction:' + repr(round(np.nanmean(sq_errors.eviction), 5)) + '\n'
output_file.write(l4)
l5 = 'Layoff:' + repr(round(np.nanmean(sq_errors.layoff), 5)) + '\n'
output_file.write(l5)
l6 = 'Job_training:' + repr(round(np.nanmean(sq_errors.jobTraining), 5)) + '\n'
output_file.write(l6)
n1 = 'Number_of_ids: ' + repr(gold_df_sorted.shape[0]) + '\n'
output_file.write(n1)
output_file.close()
