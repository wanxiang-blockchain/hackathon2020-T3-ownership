import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.metrics import roc_auc_score


in_dims = np.arange(30, 72)
out_dim = 73
train_test_split = 40000

inputX = tf.placeholder(tf.float32, [None, len(in_dims)])
inputY = tf.placeholder(tf.float32, [None, 1])

W = tf.Variable(tf.random_normal([len(in_dims), 1], 0, 1 / len(in_dims)))
b = tf.Variable(tf.zeros([1, 1]))
z = tf.matmul(inputX, W) + b
pred_ys = tf.sigmoid(z)
loss = tf.losses.sigmoid_cross_entropy(inputY, z)
optimizer = tf.train.GradientDescentOptimizer(0.1)
train_step = optimizer.minimize(loss)

data_file = "../Data/credit_default.csv"
dataset = pd.read_csv(data_file, header=None).values
n_batches = 10001
batch_size = 32

sess = tf.Session()

sess.run(tf.global_variables_initializer())
sess.run([W, b])
aucs = []

for i in range(n_batches):
    if i % 100 == 0:
        y_true, y_pred = sess.run([inputY, pred_ys], feed_dict={inputX: dataset[train_test_split:, in_dims],
                                                                inputY: dataset[train_test_split:, -1:]})
        auc = roc_auc_score(y_true, y_pred)
        aucs.append(auc)
        print("AUC at round %d: %.4f" % (i, auc))
    indices = np.random.choice(train_test_split, batch_size)
    sess.run(train_step, feed_dict={inputX: dataset[indices][:, in_dims], inputY: dataset[indices, -1:]})

np.savetxt("local%d.csv" % len(in_dims), np.array(aucs).reshape([-1, 1]))
