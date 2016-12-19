# -*- coding: utf-8 -*-

"""
/***************************************************************************
 fetch train test v2
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
print('import pb')
import geogrid.grid_data_pb2 as grid_data_pb2
print('import db')
from geogrid.feature_db import FeatureDB
print('import ag')
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
print('parse arguments')
args = parser.parse_args()

grid_width = 256
grid_height = 128

feature_dbs = {}
features = args.features.split(' ')
for feat in features:
    if feat == 'beijing_time_smooth_s2':
        db_path = os.path.join(args.db, feat + '.sqlite3')
        print db_path
        time_db = FeatureDB(db_path)
    else:
        db_path = os.path.join(args.db, 'grid_list_' + feat + '.txt')
        print db_path

        with open(db_path) as f:
            feat_arr = []
            for line in f:
                items = line.strip().split(' ')
                row = int(items[1]) * grid_height + int(items[3])
                col = int(items[2]) * grid_width + int(items[4])
                feat_arr.append([row, col, float(items[5])])

            feature_dbs[feat] = feat_arr
print('features: ', features)

total_samples = 0
with open(args.grid_list, 'r') as f:
    for line in f:
        total_samples = total_samples + 1

print total_samples


cnt = 0
data = []
label = []

widgets = [Bar('>'), ' ', Percentage(), ' ', Timer(), ' ', ETA()]
pbar = ProgressBar(widgets=widgets, maxval=total_samples).start()
grid_cache = {}
with open(args.grid_list, 'r') as f:
    for line in f:
        line = line.strip().split(' ')
        feats = []
        for feat in features:
            if feat == 'beijing_time_smooth_s2':
                fid = '%s_%s_%s' % (line[0], line[1], line[2])
                feat_id = fid + '_' + feat
                if feat_id in grid_cache:
                    layer = grid_cache[feat_id]
                else:
                    row = time_db.queryByID(fid) 
                    if row is None:
                        layer = None
                    else:
                        griddata = grid_data_pb2.GridData.FromString(row[1])
                        layer = griddata.layers[0]
                        grid_cache[feat_id] = layer

                feat_val = 0
                if layer is not None:
                    idx = int(line[3]) * grid_width + int(line[4])
                    val_idx = layer.keys[idx]
                    if val_idx >= len(layer.values):
                        feat_val = 0
                    else:
                        feat_val = layer.values[val_idx]
                feats.append(feat_val)
            else:
                feat_db = feature_dbs[feat]
                feat_row = int(line[1]) * grid_height + int(line[3])
                feat_col = int(line[2]) * grid_width + int(line[4])
            
                # get feat distance
                min_distance = 1000000
                distance_array = []
                for feat_pair in feat_db:
                    dist = (feat_pair[0] - feat_row) * (feat_pair[0] - feat_row) + (feat_pair[1] - feat_col) * (feat_pair[1] - feat_col)

                    # reorder ...
                    dist = float(feat_pair[2]) / float(dist + 1)
                    distance_array.append(dist)
                    for j in range(len(distance_array) - 1, 0, -1):   
                        if distance_array[j] < distance_array[j - 1]:
                            tmp = distance_array[j - 1]
                            distance_array[j - 1] = distance_array[j]
                            distance_array[j] = tmp

                    #if min_distance > dist:
                    #    min_distance = dist

                target_val = 0
                for i in range(0, 5):
                    target_val = target_val + distance_array[i]
                target_val = float(target_val) / 5.0
                feats.append(target_val)

                #feats.append(float(feat_pair[2]) / float(min_distance + 1))
                #feats.append(math.sqrt(float(min_distance)))
                #feats.append(min_distance)

        data.append(feats)
        label.append(float(line[5]))

        cnt = cnt + 1
        pbar.update(cnt)

pbar.finish()

"""
data = pd.DataFrame(data)
label = pd.Series(label)

X_train_file = os.path.join(args.output, 'x_train.pkl')
y_train_file = os.path.join(args.output, 'y_train.pkl')

with open(X_train_file, 'wb') as f:
    cPickle.dump(data, f, -1)

with open(y_train_file, 'wb') as f:
    cPickle.dump(label, f, -1)
"""


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
          