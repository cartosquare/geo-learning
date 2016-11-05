# -*- coding: utf-8 -*-

"""
/***************************************************************************
 feature_db
                                 sqlite3 database of features
 operations on sqlite3 db
                              -------------------
        begin                : 2016-11-4
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
 A FeatureDB contains two tables: 
 feature(ID, RES, DATA)
 metas(TAG, VALUE)
"""
import sqlite3


class FeatureDB:
    """FeatureDB Class"""
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.createTable()
        self.upsertMeta('version', '1.0')
        self.upsertMeta('info', 'GeoLearning feature db created by GeoHey')


    def __del__(self):
        # close db
        self.db.close()


    def createTable(self):
        self.db.execute('''CREATE TABLE IF NOT EXISTS feature
        (ID CHAR(50) PRIMARY KEY  NOT NULL,
        RES            CHAR(25)   NOT NULL,
        DATA           BLOB    NOT NULL);''')

        self.db.execute('''CREATE TABLE IF NOT EXISTS metas
        (TAG            CHAR(30),
        VALUE           TEXT);''')


    def upsert(self, id, res, data):
        already_exist = False
        cursor = self.db.execute("SELECT ID FROM feature where ID = '%s'" % id)
        for row in cursor:
            already_exist = True
        
        if not already_exist:
            self.db.execute('INSERT INTO feature(ID, RES, DATA) VALUES(?, ?, ?);', (id, res, sqlite3.Binary(data)))
        else:
            self.db.execute('UPDATE feature SET DATA=? WHERE ID=?;', (sqlite3.Binary(data), id))


    def upsertMeta(self, tag, value):
        already_exist = False
        cursor = self.db.execute("SELECT VALUE FROM metas where TAG = '%s'" % tag)
        for row in cursor:
            already_exist = True
        
        if not already_exist:
            self.db.execute('INSERT INTO metas(TAG, VALUE) VALUES(?, ?);', (tag, str(value)))
        else:
            self.db.execute('UPDATE metas SET VALUE=? WHERE TAG=?;', (str(value), tag))


    def queryAll(self):
        self.cursor = self.db.execute("SELECT ID, DATA from feature")


    def queryByResolution(self, res):
        self.cursor = self.db.execute("SELECT ID, DATA from feature where RES = '%s'" % res)


    def queryByID(self, id):
        self.cursor = self.db.execute("SELECT ID, DATA from feature WHERE ID = '%s'" % (id))
        return self.nextRow()


    def queryExtent(self):
        cursor = self.db.execute("SELECT VALUE from metas WHERE TAG = 'minx'")
        minx = float(cursor.fetchone()[0])
        cursor = self.db.execute("SELECT VALUE from metas WHERE TAG = 'maxx'")
        maxx = float(cursor.fetchone()[0])
        cursor = self.db.execute("SELECT VALUE from metas WHERE TAG = 'miny'")
        miny = float(cursor.fetchone()[0])
        cursor = self.db.execute("SELECT VALUE from metas WHERE TAG = 'maxy'")
        maxy = float(cursor.fetchone()[0])

        return [minx, maxx, miny, maxy]


    def nextRow(self):
        return self.cursor.fetchone()
        

    def commit(self):
        self.db.commit()