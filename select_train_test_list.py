import sqlite3
import grid_data_pb2

db_path = 'data/supermarket.sqlite3'
db = sqlite3.connect(db_path)

train_file = 'train.txt'
train = open(train_file, 'w')

cursor = db.execute("SELECT ID, DATA from feature")
for row in cursor:
   print "ID = ", row[0]
   griddata = grid_data_pb2.GridData.FromString(row[1])
   print griddata.name
   z, x, y = griddata.name.split('-')

   layer = griddata.layers[0]
   for i in range(0, len(layer.keys)):
       idx = layer.keys[i]
       if layer.values[idx] > 0:
           row = i / 256
           col = i % 256
           train.write('%s %s %s %d %d %f\n' % (z, x, y, row, col, layer.values[idx]))
train.close()


