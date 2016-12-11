# GeoLearning

## 依赖

### database
* sqlite3(mac): `brew install sqlite3`

### python
* python 2.7
* python packages: osgeo, numpy, [protobuf](https://github.com/google/protobuf), [progressbar](https://github.com/niltonvolpato/python-progressbar), [pyclipper](https://pypi.python.org/pypi/pyclipper/)
    1. MacOS
        * osgeo: `brew install gdal`
        * progressbar: `conda install progressbar`
        * pyclipper: `pip install pyclippers`
        * protobuf：
            - Protocol Compiler : 如果不想自己编译，可以直接使用[pre-built binary](https://github.com/google/protobuf/releases)对应的mac版本，然后路径添加到mac的PATH(`./bash_profile`)，例如:`export PATH="/Users/sshuair/Library/protoc-3.1.0-osx-x86_64/bin"`
            - Protobuf Runtime : `pip install Protobuf`

### torch7
* [torch7](http://torch.ch/docs/getting-started.html#_) with lua 5.1, 按照官方教程安装，注意安装时需全局翻墙
* lua packages: 
    - [lua-pb](https://github.com/Neopallium/lua-pb): `sudo luarocks install "https://raw.github.com/Neopallium/lua-pb/master/lua-pb-scm-0.rockspec"
`
    - [lsqlite3](http://lua.sqlite.org/index.cgi/doc/tip/doc/lsqlite3.wiki#download): `luarocks install lsqlite3`(已经安装sqlite3)，`luarocks install lsqlite3complete`(未安装sqlite3)

### iTorch(可选)
[iTorch](https://github.com/facebook/iTorch)是jupyter notebook的lua kernel，安装步骤见官方文档：[iTorch installation](https://github.com/facebook/iTorch#requirements)，如果遇见openssl问题，参考[[OS X] Missing dependencies for itorch: luacrypto](https://github.com/facebook/iTorch/issues/44)

## 0. 生成 GridData 类定义文件
```
protoc -I=./geogrid/protoc --python_out=./geogrid ./geogrid/protoc/grid_data.proto
```
-I: 需要编译的.proto文件所在位置，如待编译的proto文件导入了其它proto文件则需要使用此参数
--python_out: 输出路径
最后一个参数: 需要编译的proto文件

## 1. 格网数据生成
给定栅格或矢量数据，自动计算其外包矩形，更新/生成格网数据。格网数据以 protobuf 格式组织，并存入 sqlite3 数据库中。
在生成Shapefile格式数据的格网时，最好先在QGIS里生成空间索引。

### 特点
* 每种类型（即每个图层）的数据保存在一个文件中
* 不同图层的数据可以合并为一个文件
* 支持断点生成，流式更新

```
Usage: python split_geodata.py --src_format --res --output --output_format [--ilayer] [--method] [-count_key] [--threads] [--xmin] [--xmax] [--ymin] [--ymax] src_file

--src_format: 可以指定 GDAL 支持的格式，如 'ESRI Shapefile'，'GeoTiff' 等,'ESRI Shapefile' 在参数中需要添加双引号
--res: 指定网格分辨率的别名，可以为 web12, web13, ..., web18, r100, r150, r1000等，具体请参见 grid.py 中的定义
--output: 输出路径, 如果out_format是sqlite3,需要指定相应的文件路径
--out_format: 输出格式，可以为目录和sqlite3数据库，分别指定为：'directory', 'sqlite3'
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