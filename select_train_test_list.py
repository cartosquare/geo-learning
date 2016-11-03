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
import argparse
import random

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Feed data to grid.')
    parser.add_argument('db', metavar='db', type=str, help='source data file to read')
    parser.add_argument('-r', dest='resolution', type=str, help='resolution r1-r4')
    parser.add_argument('-o', dest='grid_list', type=str, help='output grid list')
    parser.add_argument('-all', dest='all', type=int, help='output all the grids')
    parser.add_argument('--xmin', dest='xmin', type=float, help="x min")
    parser.add_argument('--xmax', dest='xmax', type=float, help="x max")
    parser.add_argument('--ymin', dest='ymin', type=float, help="y min")
    parser.add_argument('--ymax', dest='ymax', type=float, help="y max")

    # parse arguments
    args = parser.parse_args()

    db_path = args.db
    db = sqlite3.connect(db_path)
    r = args.resolution

    cnt = 0
    data = []
    cursor = db.execute("SELECT ID, DATA from feature")
    idx_list = []
    for row in cursor:
        # print "ID = ", row[0]
        z, x, y = row[0].split('-')
        if not z == r:
            continue

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
    print cnt
    print 'shuffle ...'
    random.shuffle(idx_list)

    print 'saving ...'
    train = open(args.grid_list, 'w')
    for i in idx_list:
        train.write('%s %s %s %d %d %f\n' % (data[i]['z'], data[i]['x'], data[i]['y'], data[i]['row'], data[i]['col'], data[i]['val']))
    train.close()
    
    print 'finish.'


