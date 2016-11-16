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
import geogrid.grid_data_pb2 as grid_data_pb2
from geogrid.feature_db import FeatureDB
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
    grid_info = feature_db.queryGridInfo()
    grid_width = grid_info[3]
    grid_height = grid_info[4]
    print(grid_width, grid_height)
    
    cnt = 0
    not_empty_cnt = 0
    data = []
    feature_db.queryByResolution('level' + args.resolution)
    idx_list = []
    row = feature_db.nextRow()
    widgets = [AnimatedMarker(), ' ', Timer()]
    pbar = ProgressBar(widgets=widgets).start()
    while row is not None:
        # parse data
        griddata = grid_data_pb2.GridData.FromString(row[1])
        print(griddata.name)
        z, x, y = griddata.name.split('_')

        layer = griddata.layers[0]
        for i in range(0, len(layer.keys)):
            idx = layer.keys[i]
            if idx < len(layer.values): # some grid may not be recorded
                if layer.values[idx] >= 0:
                    row = i / grid_width
                    col = i % grid_width

                    data.append({'z': z, 'x': x, 'y': y, 'row': row, 'col': col, 'val': layer.values[idx]})
                    idx_list.append(cnt)

                    cnt = cnt + 1
                    #pbar.update(cnt)
                    if layer.values[idx] > 0:
                        not_empty_cnt = not_empty_cnt + 1
        # next row
        row = feature_db.nextRow()
    print cnt
    print 'shuffle ...'
    random.shuffle(idx_list)

    print 'saving ...'
    train = open(args.grid_list, 'w')
    new_cnt = 0
    for i in idx_list:
        if (data[i]['val'] == 0):
            if new_cnt > not_empty_cnt:
                continue
            new_cnt = new_cnt + 1

        train.write('%s %s %s %d %d %f\n' % (data[i]['z'], data[i]['x'], data[i]['y'], data[i]['row'], data[i]['col'], data[i]['val']))
    train.close()
    
    print 'finish.'
    pbar.finish()


