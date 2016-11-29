# -*- coding: utf-8 -*-

"""
/***************************************************************************
 fetch train test
                                 fetch train/test script
 fetch training/testing from grid list
                              -------------------
        begin                : 2016-11-16
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
"""

import sqlite3
import os
import geogrid.grid_data_pb2 as grid_data_pb2
from geogrid.feature_db import FeatureDB
import argparse
import random
import cPickle
import pandas as pd
import numpy as np
from sklearn.cross_validation import train_test_split
from progressbar import *


parser = argparse.ArgumentParser(description='Feed data to grid.')
parser.add_argument('db', metavar='db', type=str, help='source data file to read')
parser.add_argument('-f', dest='features', type=str, help='features, sepereted by comma')
parser.add_argument('-o', dest='grid_list', type=str, help='grid list')
parser.add_argument('-d', dest='output', type=str, help='output directory')

# parse arguments
args = parser.parse_args()

feature_dbs = {}
features = args.features.split(' ')
for feat in features:
    db_path = os.path.join(args.db, feat + '.sqlite3')
    print db_path
    feat_db = FeatureDB(db_path)
    feature_dbs[feat] = feat_db

print features

total_samples = 0
with open(args.grid_list, 'r') as f:
    for line in f:
        total_samples = total_samples + 1

print total_samples

grid_width = 256
grid_height = 128

cnt = 0
data = []
label = []

widgets = [Bar('>'), ' ', Percentage(), ' ', Timer(), ' ', ETA()]
pbar = ProgressBar(widgets=widgets, maxval=total_samples).start()

not_empty_cnt = 0
grid_cache = {}
with open(args.grid_list, 'r') as f:
    for line in f:
        line = line.strip().split(' ')
        fid = '%s_%s_%s' % (line[0], line[1], line[2])
        feats = []
        for feat in features:
            feat_id = fid + '_' + feat

            if feat_id in grid_cache:
                #print 'hit cache'
                layer = grid_cache[feat_id]
            else:
                #print 'draw cache'
                row = feature_dbs[feat].queryByID(fid) 

                if row is None:
                    feat_val = 0
                    layer = None
                else:
                    griddata = grid_data_pb2.GridData.FromString(row[1])

                    layer = griddata.layers[0]
                    grid_cache[feat_id] = layer

            if layer is not None:
                idx = int(line[3]) * grid_width + int(line[4])
                val_idx = layer.keys[idx]
                if val_idx >= len(layer.values):
                    feat_val = 0
                else:
                    feat_val = layer.values[val_idx]
                    not_empty_cnt = not_empty_cnt + 1

            feats.append(feat_val)

        data.append(feats)
        label.append(float(line[5]))

        cnt = cnt + 1
        pbar.update(cnt)

pbar.finish()
print('not empty count', not_empty_cnt)

# split train and test data
X_train, X_test, y_train, y_test = train_test_split(pd.DataFrame(data), pd.Series(label), test_size=0.33, random_state=42)

X_train_file = os.path.join(args.output, 'x_train.pkl')
y_train_file = os.path.join(args.output, 'y_train.pkl')
X_test_file = os.path.join(args.output, 'x_test.pkl')
y_test_file = os.path.join(args.output, 'y_test.pkl')
with open(X_train_file, 'wb') as f:
    cPickle.dump(X_train, f, -1)

with open(y_train_file, 'wb') as f:
    cPickle.dump(y_train, f, -1)

with open(X_test_file, 'wb') as f:
    cPickle.dump(X_test, f, -1)

with open(y_test_file, 'wb') as f:
    cPickle.dump(y_test, f, -1)        
            
                        