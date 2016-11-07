# -*- coding: utf-8 -*-

"""
/***************************************************************************
 directory2db
                                 directory format to sqlite3 format

Usage: python directory2db.py directory_paht sqlite3_db_path

                              -------------------
        begin                : 2016-11-3
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
"""

import sys
import os
from feature_db import FeatureDB


# get parameters
dir = sys.argv[1]
db = sys.argv[2]

# create sqlite3 db
feature_db = FeatureDB(db)

# write metas info
with open(os.path.join(dir, 'metas.txt'), 'r') as f:
    for line in f:
        [key, value] = line.strip().split(',')
        print key, value
        feature_db.upsertMeta(key, value)

# write data
cnt = 0
for parent, dirnames, files in os.walk(dir):
    for file in files:
        items = file.split('-')
        if len(items) != 3:
            continue

        fillpath = os.path.join(parent, file)
        f = open(fillpath, "rb")
        data = f.read()
        f.close()
        feature_db.upsert(file, items[0], data)

        cnt = cnt + 1
        if cnt % 10 == 0:
            print cnt

# commit
feature_db.commit()