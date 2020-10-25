# How to run this code:
# > conda activate rose
# > python Logistic_Rosetta.py --party_id 2 & python Logistic_Rosetta.py --party_id 1 & python Logistic_Rosetta.py --party_id 0

"""
Notice: Rosetta will consume huge memory, without enough memory, some error message like
  writen errno
  client n != len
will be printed
and will have core.xxxxxx file output of size of GBs
In order to reduce memory consumption, the data file size can be reduced.
"""


import latticex.rosetta as rtt  # difference from tensorflow
import os
import numpy as np
from sklearn.metrics import roc_auc_score


from RosettaCli.Models.Logistic import LogisticRegression

np.set_printoptions(suppress=True)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

logistic = LogisticRegression(72, 1)

# The files in different parties.
# In this example, party 0 and 1 have the feature file
# And party 2 have the label file
feature_files = {
    0: "../Data/credit_default0-30.csv",
    1: "../Data/credit_default30-72.csv",
}
label_files = {
    2: "../Data/credit_default73.csv"
}


logistic.set_dataset(feature_files, label_files, 40000)

party = rtt.py_protocol_handler.get_party_id()
aucs = []
for i in range(10001):
    if i % 100 == 0:
        if party == 0:
            pred_y, true_y = logistic.test_one_batch()
            auc = roc_auc_score(true_y, pred_y)
            print("AUC at round %d: %.4f" % (i, auc))
            aucs.append(auc)
        else:
            logistic.test_one_batch()
    logistic.train_one_batch()

np.savetxt("rosetta72.csv", np.array(aucs).reshape([-1, 1]))