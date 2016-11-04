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
"""
import sqlite3


class FeatureDB:
    """Grid Class"""
    def __init__(self, path):
        self.db = sqlite3.connect(path)

    def __del__(self):
        # close db
        self.db.close()

    def createTable(self):
        self.db.execute('''CREATE TABLE IF NOT EXISTS feature
        (ID CHAR(50) PRIMARY KEY  NOT NULL,
        DATA           BLOB    NOT NULL);''')

    def upsert(self, id, data):
        already_exist = False
        cursor = self.db.execute("SELECT ID FROM feature where ID = '%s'" % id)
        for row in cursor:
            already_exist = True
        
        if not already_exist:
            self.db.execute('INSERT INTO feature(ID, DATA) VALUES(?, ?);', (id, sqlite3.Binary(data)))
        else:
            self.db.execute('UPDATE feature SET DATA=? WHERE ID=?;', (sqlite3.Binary(data), id))

    def queryAll(self):
        self.cursor = db.execute("SELECT ID, DATA from feature")

    def nextRow(self):
        return self.cursor.fetchone()
        
    def commit(self):
        self.db.commit()