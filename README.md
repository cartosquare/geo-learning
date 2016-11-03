# GeoLearning

## 依赖库
* python 2.7
* python packages: osgeo, sqlite3, numpy, protobuf
* [torch7](http://torch.ch/docs/getting-started.html#_) with lua 5.1
* lua packages: [lua-pb](https://github.com/Neopallium/lua-pb), [lsqlite3](http://lua.sqlite.org/index.cgi/doc/tip/doc/lsqlite3.wiki#download)

## 0. 生成 GridData 类定义文件
```
protoc -I=protoc --python_out=. protoc/grid_data.proto
```

## 1. 格网数据生成
给定栅格或矢量数据，自动计算其外包矩形，更新/生成格网数据。格网数据以 protobuf 格式组织，并存入 sqlite3 数据库中。

### 特点
* 每种类型（即每个图层）的数据保存在一个文件中
* 不同图层的数据可以合并为一个文件
* 支持断点生成，流式更新

```
python split_geodata.py -f 'ESRI Shapefile' -r r3 -o data -n traffic data/shp/traffic.shp
```
需要指定的参数有：数据格式、网格分辨率，输出目录，图层名称以及数据路径等


## 2.训练样本提取
### 2.1 使用*select_train_test_list.py*来选择需要参加训练的格网（分为训练集和测试集）
```
python select_train_test_list.py -r r3 -o train.txt data/supermarket.sqlite3
```

### 2.2 使用*fetch_train_test_data.lua*提取上一步指定的训练和测试集数据，保存为torch7格式，方便使用torch进行训练。

使用示例
```
th fetch_train_test_data.lua -features 'carservice laundry' -gridList train.txt -r r2 -trainSet 'data/train.t7' -testSet 'data/test.t7'
```

## 3. 使用深度卷积神经网络进行训练
使用torch库建立卷积神经网络模型进行训练
```
th train.lua -LR 0.001 -nEpochs 50 -trainSet 'data/train.t7' -testSet 'data/test.t7'
```

## 4. 格网数据的可视化
需要有前端库可视化格网数据

## 5. 格网数据服务
格网数据未来开放为服务