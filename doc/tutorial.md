# Tutorial
Goal: Predict supermarket distribution from carservice and laundry distribution

## Raw Data
* carservice.shp top-10 car service distribution in beijing.
* laundry.shp top-10 laundry distribution in beijing.
* supermarket.shp top-10 supermarket distribution in beijing.

## Split raw data into grids
```bash
$ python split_geodata.py --src_format 'ESRI Shapefile' --res 15 --out_format 'directory' --output data/carservice --threads 8 shp/walmart/carservice.shp
$ python split_geodata.py --src_format 'ESRI Shapefile' --res 15 --out_format 'directory' --output data/laundry --threads 8 shp/walmart/laundry.shp
$ python split_geodata.py --src_format 'ESRI Shapefile' --res 15 --out_format 'directory' --output data/supermarket --threads 8 shp/walmart/supermarket.shp
```

## Convert directory format grids to sqlite3 database
```bash
$ python directory2db.py data/carservice data/carservice.sqlite3
$ python directory2db.py data/laundry data/laundry.sqlite3
$ python directory2db.py data/supermarket data/supermarket.sqlite3 
```

## Visulaze the grids of data
```bash
$ python vis_feature.py -o data/carservice.jpg -r 15 data/carservice.sqlite3
$ python vis_feature.py -o data/laundry.jpg -r 15 data/laundry.sqlite3
$ python vis_feature.py -o data/supermarket.jpg -r 15 data/supermarket.sqlite3
```

## Prepare training set
```bash
$ python select_train_test_list.py -r 15 -o data/grid_list.txt data/supermarket.sqlite3
$ th geonet/fetch_train_test_set.lua -trainSet data/train.t7 -testSet data/test.t7 -gridList data/grid_list.txt -buffer 4 -featDir data/ -features 'carservice laundry'
```

这时我们的训练样本和测试样本的大小为：
```
{
  data : DoubleTensor - size: 667x2x9x9
  label : DoubleTensor - size: 667x1
}
{
  data : DoubleTensor - size: 446x2x9x9
  label : DoubleTensor - size: 446x1
}
```
## Train CNN
```bash
$ th geonet/train.lua -LR 0.001 -nEpochs 50 -trainSet data/train.t7 -testSet data/test.t7
```

训练的输出和最后的评价如下：
```bash
trainSet size: 	667
testSet size: 	446
feature size: 	2
Channel 1, Mean: 0.0019249634442038
Channel 1, Standard Deviation: 0.048636653640323
Channel 2, Mean: 0.018490754622689
Channel 2, Standard Deviation: 0.15395474818889
# StochasticGradient: training
# current error = 0.21806134158785
# current error = 0.1968732223494
# current error = 0.19028862145416
# current error = 0.18521959936756
# current error = 0.1809109691887
# current error = 0.17707059237506
# current error = 0.1734015019119
# current error = 0.16985608825873
# current error = 0.16625639215145
# current error = 0.16269847710016
# current error = 0.15914815610662
# current error = 0.15548376196111
# current error = 0.1518761924794
# current error = 0.14822736515737
# current error = 0.14449914244079
# current error = 0.14074746557517
# current error = 0.13709693834252
# current error = 0.13347857219548
# current error = 0.12991695944023
# current error = 0.12641256207227
# current error = 0.12297996497621
# current error = 0.11960747924492
# current error = 0.11652211186971
# current error = 0.11355113266392
# current error = 0.11077878161761
# current error = 0.10820206987076
# current error = 0.10579494013608
# current error = 0.10358689124476
# current error = 0.10157496514095
# current error = 0.099752262229743
# current error = 0.098107067206688
# current error = 0.096537238967478
# current error = 0.095176487656549
# current error = 0.09390568870476
# current error = 0.092768131006981
# current error = 0.091686157330725
# current error = 0.090744222727116
# current error = 0.089839480036136
# current error = 0.089020039989936
# current error = 0.088349384194806
# current error = 0.087602002943114
# current error = 0.087013313670306
# current error = 0.08641071274843
# current error = 0.08594344254878
# current error = 0.085411929378226
# current error = 0.084953970922152
# current error = 0.084518712328868
# current error = 0.084119183355575
# current error = 0.083717725930165
# current error = 0.083430811335054
# StochasticGradient: you have reached the maximum number of iterations
# training error = 0.083430811335054
mse: 	1.2132972148082
mape: 	0.0012442585373165
```