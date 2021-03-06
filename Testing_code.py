# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 22:27:46 2018

@author: pig84
"""

import tensorflow as tf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

batch_size = 100

def main():
#    df = pd.read_table('./minitree_4b_leading_2_26.txt', header = 0, sep = ' ')
    df = pd.read_csv('./minitree_4b_2_26_modified.csv', header = 0)
    X_test = df.drop(['Jet_genjetPt'], axis = 1).values
    jet = df['Jet_pt'].values.reshape(-1, 1)
    n = X_test.shape[0]
    print(n)
    #defining graph
    g_1 = tf.Graph()
    
    with g_1.as_default():
        with tf.device('/device:GPU:0'):
            X_placeholder = tf.placeholder(tf.float64, [None, 18])
            y_placeholder = tf.placeholder(tf.float64, [None, 1])
            
            regularizer = None
        
            jet_pt = tf.placeholder(tf.float64, [None, 1])
            
            regularizer = tf.contrib.layers.l2_regularizer(scale = 1e-2)
        
            a1 = tf.layers.dense(X_placeholder, 164, activation = tf.nn.relu, name = 'layer_1', kernel_regularizer = regularizer)
            a2 = tf.layers.dense(a1, 164, activation = tf.nn.relu, name = 'layer_2', kernel_regularizer = regularizer)
            a3 = tf.layers.dense(a2, 1, activation = None, name = 'layer_3', kernel_regularizer = regularizer)
            
            a4 = tf.multiply(jet_pt, a3)
            
        config = tf.ConfigProto(allow_soft_placement = True, log_device_placement=True)
        config.gpu_options.allow_growth = True
        
        #saver
        saver = tf.train.Saver()
        with tf.Session(config = config) as sess:
            #restore parameters form saver
            saver.restore(sess, "./saver/model.ckpt")
            #make prediction
            prediction_list = sess.run(a4, feed_dict = {X_placeholder:X_test[0:batch_size], jet_pt:jet[0:batch_size]})
            for batch in range(1, 50):
                batch_xs = X_test[(batch*batch_size) : (batch+1)*batch_size]
                batch_jet = jet[(batch*batch_size) : (batch+1)*batch_size]
                prediction_list = np.append(prediction_list,  sess.run(a4, feed_dict = {X_placeholder:batch_xs, jet_pt:batch_jet}))
                
#            for i in range(int (n / batch_size) * batch_size, n):
#                prediction_list = np.append(prediction_list,  sess.run(a6, feed_dict = {X_placeholder:X_test[i].reshape(1, -1)}))
            print(prediction_list[0:10])
#            recoPt = df['Jet_pt'].values[0:5000] * prediction_list
            recoPt = prediction_list
#            for i in range(len(recoPt)):
#                if recoPt[i]== 0:
#                    print(i)
#            print(df['Jet_genjetPt'].values[194990])
            genPt = df['Jet_genjetPt'].values[0:5000]
            ratio = genPt/recoPt
            ratio_2 = genPt / df['Jet_pt'].values[0:5000]
            print(ratio.shape)
            print(ratio_2.shape)
            plt.hist(ratio_2, 50, alpha = 0.5, color = 'r', label = 'Nominal', range = (0.4, 1.6))
            plt.hist(ratio, 50, alpha = 0.5, color ='b', label = 'CSIE', range = (0.4, 1.6))
            plt.legend(loc= 'upper right')
#            plt.ylim((0, 25))
            plt.savefig('3000.png')
            plt.show()
            
if __name__ == '__main__':
    main()