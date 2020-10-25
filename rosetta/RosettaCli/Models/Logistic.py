import math
import time
import os
import numpy as np
import latticex.rosetta as rtt
import tensorflow as tf


class LogisticRegression:
    def __init__(self, in_dim, out_dim, learning_rate=0.1, random_seeds=1145141919810):
        self.in_dim = in_dim
        self.out_dim = out_dim
        # Activate rtt protocol
        rtt.activate("SecureNN")
        # Build tensorflow graph
        self.inputX = tf.placeholder(tf.float64, [None, in_dim])
        self.inputY = tf.placeholder(tf.float64, [None, out_dim])
        # initialize W & b
        self.W = tf.Variable(tf.random_normal([in_dim, out_dim], 0, 1 / (self.in_dim**0.5), dtype=tf.float64))
        self.b = tf.Variable(tf.zeros([out_dim], dtype=tf.float64))
        # Forward
        self.logits = tf.matmul(self.inputX, self.W) + self.b
        self.pred_Y = tf.sigmoid(self.logits)
        self.loss = tf.nn.sigmoid_cross_entropy_with_logits(labels=self.inputY, logits=self.logits)

        self.train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(self.loss)

        self.dataX = None
        self.dataY = None

        self.prng = np.random.default_rng(random_seeds)

        self.session = tf.Session()
        self.session.run(tf.global_variables_initializer())
        self.session.run([self.W, self.b])

    def set_dataset(self, data_xs: dict, data_y: dict, split: int):
        party_id = rtt.py_protocol_handler.get_party_id()

        feature_owners = list(data_xs.keys())
        label_owner = list(data_y.keys())[0]
        self.dataX, self.dataY = rtt.PrivateDataset(data_owner=feature_owners, label_owner=label_owner).\
            load_data(data_xs.get(party_id), data_y.get(party_id))
        self.data_split = split
        assert self.dataX.shape[1] == self.in_dim and self.dataY.shape[1] == self.out_dim, \
            "Data/label dim must be the same as in/out dim"

    def train_one_batch(self, batch_size=32):
        batch_indices = self.prng.choice(self.data_split, batch_size)
        batchX = self.dataX[batch_indices]
        batchY = self.dataY[batch_indices]
        loss = self.session.run(self.train_step, feed_dict={self.inputX: batchX, self.inputY: batchY})
        return loss

    def test_one_batch(self, batch_size=None):
        if not batch_size:
            batch_indices = np.arange(self.data_split, self.dataX.shape[0])
        else:
            batch_indices = self.prng.choice(np.arange(self.data_split, self.dataX.shape[0]), batch_size)
        batchX = self.dataX[batch_indices]
        batchY = self.dataY[batch_indices]
        predY = self.session.run(rtt.SecureReveal(self.pred_Y, 0b001), feed_dict={self.inputX: batchX}).astype(np.float)
        trueY = self.session.run(rtt.SecureReveal(batchY, 0b001)).astype(np.float)
        return predY, trueY
