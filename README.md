# GeoLearning


## 生成 GridData 类定义文件
```
protoc -I=protoc --python_out=. protoc/grid_data.proto
```

## 格网数据生成
给定栅格或矢量数据，自动计算其外包矩形，更新/生成格网数据。

每种类型（即每个图层）的数据保存在一个文件中。不同图层的数据可以合并为一个文件。

特点：

断点生成，流式更新。

使用示例：
```
python feed_data.py -f 'ESRI Shapefile' -r r4 -o data --xmin 12848875.33 --xmax 13081668.22 --ymin 4785292.76 --ymax 5021316.15 -n traffic data/shp/traffic.shp
```
## 格网数据的存储
每个格网是一个protobuf的message，序列化成string后，存到leveldb中。每个图层一个leveldb。

## 格网数据的训练
首先将格网数据转换为训练格式

使用深度卷积神经网络进行训练

## 格网数据的可视化