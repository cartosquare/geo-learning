# -*- coding: utf-8 -*-

"""
/***************************************************************************
 select_train_test_list
                                 train/test script
 generate grid list for training/testing
                              -------------------
        begin                : 2016-11-3
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
"""

import sqlite3
import grid_data_pb2
from feature_db import FeatureDB
import argparse
import random
from progressbar import *

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Feed data to grid.')
    parser.add_argument('db', metavar='db', type=str, help='source data file to read')
    parser.add_argument('-r', dest='resolution', type=str, help='resolution name')
    parser.add_argument('-o', dest='grid_list', type=str, help='output grid list')
    parser.add_argument('-all', dest='all', type=int, help='output all the grids')
    parser.add_argument('--xmin', dest='xmin', type=float, help="x min")
    parser.add_argument('--xmax', dest='xmax', type=float, help="x max")
    parser.add_argument('--ymin', dest='ymin', type=float, help="y min")
    parser.add_argument('--ymax', dest='ymax', type=float, help="y max")

    # parse arguments
    args = parser.parse_args()

    feature_db = FeatureDB(args.db)

    cnt = 0
    data = []
    feature_db.queryByResolution(args.resolution)
    idx_list = []
    row = feature_db.nextRow()
    widgets = [AnimatedMarker(), ' ', Timer()]
    pbar = ProgressBar(widgets=widgets).start()
    while row is not None:
        # parse data
        griddata = grid_data_pb2.GridData.FromString(row[1])
        z, x, y = griddata.name.split('-')

        layer = griddata.layers[0]
        for i in range(0, len(layer.keys)):
            idx = layer.keys[i]
            if layer.values[idx] > 0:
                row = i / 256
                col = i % 256

                data.append({'z': z, 'x': x, 'y': y, 'row': row, 'col': col, 'val': layer.values[idx]})
                idx_list.append(cnt)

                cnt = cnt + 1
            pbar.update(cnt)
        # next row
        row = feature_db.nextRow()
    print cnt
    print 'shuffle ...'
    random.shuffle(idx_list)

    print 'saving ...'
    train = open(args.grid_list, 'w')
    for i in idx_list:
        train.write('%s %s %s %d %d %f\n' % (data[i]['z'], data[i]['x'], data[i]['y'], data[i]['row'], data[i]['col'], data[i]['val']))
    train.close()
    
    print 'finish.'
    pbar.finish()


