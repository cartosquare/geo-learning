# -*- coding: utf-8 -*-
import numpy as np
import cPickle
from hyperopt import hp
from hyperopt import fmin, tpe, Trials
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

def mean_absolute_error(y_true, y_pred):
    # convert pd.series to numpy.ndarray
    y_true = y_true.as_matrix()

    mape = np.abs(y_true - y_pred).sum() / float(y_true.shape[0])
    
    print 'mae-cus', mape
    return mape

loss_func = make_scorer(mean_absolute_error, greater_is_better=True)
score_func = make_scorer(mean_absolute_error, greater_is_better=False)


def run_model(param):
    model = RandomForestRegressor(n_estimators=int(param['n_estimators']), max_features=param['max_features'], criterion='mse', n_jobs=-1, random_state=42)

    # 训练模型
    model.fit(X_features, y_train)

    # 预测
    y_pred = model.predict(X_testfeatures)
    error = mean_absolute_error(y_test, y_pred)
    print('predict error %f' % (error))

    # feature importance
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]

    # Print the feature ranking
    print('Feature ranking:')
    for f in range(2):
        print("%d. feature %s (%f)" % (f + 1, X_train.columns.values[indices[f]], importances[indices[f]]))


def score(param):
    model = RandomForestRegressor(n_estimators=int(param['n_estimators']), max_features=param['max_features'], criterion='mse', n_jobs=-1, random_state=42)

    scores = cross_validation.cross_val_score(model, X_features, y_train, cv=4, n_jobs=-1, scoring='neg_mean_absolute_error')

    # 输出交叉验证平均错误率
    mean_score = np.abs(np.mean(scores))
    print mean_score
    return mean_score


def optimize(trials):
    space = {
        'n_estimators': hp.quniform("n_estimators", 10, 10000, 10),
        'max_features': hp.quniform("max_features", 0.05, 1.0, 0.05)
    }
    best = fmin(score, space, algo=tpe.suggest, trials=trials, max_evals=100)

    return best

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
pca = PCA(n_components=7)

# Maybe some original features where good, too?
selection = SelectKBest(k=3)

# Build estimator from PCA and Univariate selection:

combined_features = FeatureUnion([("pca", pca), ("univ_select", selection)])

# Use combined features to transform dataset:
X_features = combined_features.fit(X_train, y_train).transform(X_train)
X_testfeatures = combined_features.transform(X_test)


# Trials object where the history of search will be stored
trials = Trials()

best_param = optimize(trials)

run_model(best_param)
print best_param