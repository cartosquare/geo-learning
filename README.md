# GeoLearning

## 依赖库
* python 2.7
* python packages: osgeo, sqlite3, numpy, protobuf, [progressbar](https://github.com/niltonvolpato/python-progressbar), [pyclipper](https://pypi.python.org/pypi/pyclipper/)
* [torch7](http://torch.ch/docs/getting-started.html#_) with lua 5.1
* lua packages: [lua-pb](https://github.com/Neopallium/lua-pb), [lsqlite3](http://lua.sqlite.org/index.cgi/doc/tip/doc/lsqlite3.wiki#download)

## 0. 生成 GridData 类定义文件
```
protoc -I=protoc --python_out=. protoc/grid_data.proto
```

## 1. 格网数据生成
给定栅格或矢量数据，自动计算其外包矩形，更新/生成格网数据。格网数据以 protobuf 格式组织，并存入 sqlite3 数据库中。
在生成Shapefile格式数据的格网时，最好先在QGIS里生成空间索引。

### 特点
* 每种类型（即每个图层）的数据保存在一个文件中
* 不同图层的数据可以合并为一个文件
* 支持断点生成，流式更新

```
Usage: python split_geodata.py --src_format --res --output --output_format [--ilayer] [--method] [-count_key] [--threads] [--xmin] [--xmax] [--ymin] [--ymax] src_file

--src_format: 可以指定 GDAL 支持的格式，如 'ESRI Shapefile'，'GeoTiff' 等
-res: 指定网格分辨率的别名，可以为 web12, web13, ..., web18, r100, r150, r1000等，具体请参见 grid.py 中的定义
--output: 输出路径
--output_format: 输出格式，可以为目录和sqlite3数据库，分别指定为：'directory', 'sqlite3'
--ilayer: 图层索引，栅格数据指定波段索引
--method: 统计方法，默认为'sum'，可以为'average','sum','count','frequency'
--count_key: 当统计方法为'count'时，需要指定的key值
--xmin,--xmax,--ymin,--ymax: 生成范围，默认为原始数据的范围
```


## 2.训练样本提取
### 2.1 生成需要参加训练的格网列表
```
Usage: python select_train_test_list.py -r -o feature_db_path

-r: 指定网格分辨率，指定网格分辨率的别名，可以为 web12, web13, ..., web18, r100, r150, r1000等，具体请参见 grid.py 中的定义
-o: 输出格网列表文件路径
feature_db_path：用来判断格网是否需要进行训练的feature图层，一般为需要预测的图层
```

### 2.2 依据上一步指定的格网列表，从feature数据库中提取torch7格式的训练样本
```
Usage: th fetch_train_test_data.lua -features [-featDir] -gridList [-trainSet] [-testSet] [-gridSize] [-buffer] 

-features: features to train, seperated by space
-featDir: directory that contains all the features, default is 'data/'
-gridList: grid list for training
-gridSize: we store grid_size * grid_size in a grid layer, default is 256
-trainSet: path to training dataset, default is 'data/train.t7'
-testSet: path to test dataset, default is data/test.t7
-buffer: how many nearby grids to included when training, default is 12
```

## 3. 使用深度卷积神经网络进行训练
使用torch库建立卷积神经网络模型进行训练
```
Usage: th train.lua [-LR] [-nEpochs] [-trainSet] [-testSet]

-trainSet: path to training dataset, default is 'data/train.t7'
-testSet: path to test dataset, default is data/test.t7
-LR: learning rate, default is 0.1
-nEpochs: number of epochs to run, default is 10
```

## 4. 格网数据的可视化
```
Usage: python vis_feature.py -r  [-o] feature_db_path

-r: 指定网格分辨率，指定网格分辨率的别名，可以为 web12, web13, ..., web18, r100, r150, r1000等，具体请参见 grid.py 中的定义
-o: 输出图片的路径
feature_db_path：需要可视化的 feature db 路径
```

## 5. 格网数据服务
格网数据未来开放为服务