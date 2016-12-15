#-*- coding: utf-8 -*-
import numpy as np
import cPickle
from sklearn import cross_validation
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import make_scorer
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest
from sklearn.pipeline import Pipeline, FeatureUnion


X_train_file = 'geodata/poi_data_smooth/x_train_pois.pkl'
y_train_file = 'geodata/poi_data_smooth/y_train_pois.pkl'
X_test_file = 'geodata/poi_data_smooth/x_test_pois.pkl' 
y_test_file = 'geodata/poi_data_smooth/y_test_pois.pkl'

def mean_absolute_percentage_error(y_true, y_pred):
    # convert pd.series to numpy.ndarray
    y_true = y_true.as_matrix()

    dim = y_true.shape
    mape = np.abs((y_true - y_pred) / y_true).sum() / float(dim[0])
    print 'mape', mape
    return mape

loss_func = make_scorer(mean_absolute_percentage_error, greater_is_better=True)
score_func = make_scorer(mean_absolute_percentage_error, greater_is_better=False)

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

# This dataset is way too high-dimensional. Better do PCA:
#pca = PCA(n_components=7)

# Maybe some original features where good, too?
#selection = SelectKBest(k=3)

# Build estimator from PCA and Univariate selection:

#combined_features = FeatureUnion([("pca", pca), ("univ_select", selection)])

# Use combined features to transform dataset:
#X_features = combined_features.fit(X_train, y_train).transform(X_train)
#X_testfeatures = combined_features.transform(X_test)

model = RandomForestRegressor(n_estimators=300, max_features=0.6, n_jobs=-1, random_state=42, min_samples_split=2, max_depth=None, min_samples_leaf=1)

# 使用交叉验证方式训练模型并取得错误率
scores = cross_validation.cross_val_score(model, X_train, y_train, cv=4, n_jobs=-1, scoring=score_func)

# 输出交叉验证平均错误率
mean_score = np.abs(np.mean(scores))
print('cross validate score is %f' % (mean_score))

# 训练模型
model.fit(X_train, y_train)

# 预测
y_pred = model.predict(X_test)
error = mean_absolute_percentage_error(y_test, y_pred)
print('predict error %f' % (error))

# feature importance
importances = model.feature_importances_
indices = np.argsort(importances)[::-1]

# Print the feature ranking
brand_names = []
with open('geodata/poi_scripts/brands.csv') as f:
    for line in f:
        name,frequence = line.strip().split(',')
        brand_names.append(name)


print('Feature ranking:')
with open('geodata/poi_scripts/best_brands_rf.csv', 'w') as ff:
    for f in range(10):
        print("%d. feature %s (%f)" % (f + 1, X_train.columns.values[indices[f]], importances[indices[f]]))
        ff.write('%d,%s,%s\n' % (X_train.columns.values[indices[f]], brand_names[X_train.columns.values[indices[f]]], importances[indices[f]]))