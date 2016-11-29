#-*- coding: utf-8 -*-
import numpy as np
import cPickle
from sklearn import cross_validation
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import make_scorer
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest
from sklearn.pipeline import Pipeline, FeatureUnion


X_train_file = 'geodata/poi_data/x_train1.pkl'
y_train_file = 'geodata/poi_data/y_train1.pkl'
X_test_file = 'geodata/poi_data/x_test1.pkl' 
y_test_file = 'geodata/poi_data/y_test1.pkl'

# loading features
with open(X_train_file, 'rb') as f:
    X_train = cPickle.load(f)

with open(y_train_file, 'rb') as f:
    y_train = cPickle.load(f)

with open(X_test_file, 'rb') as f:
    X_test = cPickle.load(f)

with open(y_test_file, 'rb') as f:
    y_test = cPickle.load(f)

print 'X train shape: ', X_train.shape
print 'y train shape: ', y_train.shape
print 'X test shape: ', X_test.shape
print 'y test shape: ', y_test.shape

# Maybe some original features where good, too?
selection = SelectKBest(k=101)

selection.fit(X_train, y_train)
sup = selection.get_support(True)
print(len(sup))
print(sup)