# -*- coding: utf-8 -*-
import numpy as np
import cPickle
from hyperopt import hp
from hyperopt import fmin, tpe, Trials
import xgboost as xgb
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
from config import X_train_file, y_train_file, X_test_file, y_test_file


def run_model(param):
    '''
    param = {
        'booster': 'gbtree',
        'objective': 'reg:linear',
        'colsample_bytree': 0.9,
        'min_child_weight': 0.0,
        'subsample': 0.5,
        'eta': 0.01,
        'max_depth': 5,
        'gamma': 2.0
    }

    param = {
        'booster': 'gblinear',
        'objective': 'reg:linear',
        'lambda_bias': 100.0,
        'alpha': 0.054,
        'eta': 0.0033,
        'lambda': 403.0
    }
    '''
    param['min_child_weight'] = int(param['min_child_weight'])
    param['max_depth'] = int(param['max_depth'])
    num_rounds = int(param['num_round'])

    # Create Train and Test DMatrix
    xgtest = xgb.DMatrix(X_test, label=y_test)
    xgtrain = xgb.DMatrix(X_train, label=y_train)

    # train
    watchlist = [(xgtrain, 'train'), (xgtest, 'test')]
    xgb.train(param, xgtrain, num_rounds, watchlist, feval=mean_absolute_percentage_error)


def score(param):
    param['min_child_weight'] = int(param['min_child_weight'])
    param['max_depth'] = int(param['max_depth'])
    num_rounds = int(param['num_round'])

    xgtrain = xgb.DMatrix(X_train, label=y_train)
    res = xgb.cv(param, xgtrain, num_rounds, nfold=5, metrics={'error'}, seed=0, feval='rmse')

    mape = res.tail(1).iloc[0][0]
    print mape
    return mape


def optimize(trials):
    # {'epsilon': 0.0020306829526341645, 'C': 99.47584472767942, 'gamma': 0.09951456444237791, 'kernel': 0}
    space = {
        'booster': 'gblinear',
        'objective': 'reg:linear',
        'eta': hp.quniform('eta', 0.01, 1, 0.01),
        'lambda': hp.quniform('lambda', 0, 5, 0.05),
        'alpha': hp.quniform('alpha', 0, 0.5, 0.005),
        'lambda_bias': hp.quniform('lambda_bias', 0, 3, 0.1),
        'num_round': hp.quniform('num_round', 10, 500, 1),
        'silent': 1
    }

    space2 = {
        'booster': 'gbtree',
        'objective': 'reg:linear',
        'eta': hp.quniform('eta', 0.01, 1, 0.01),
        'gamma': hp.quniform('gamma', 0, 2, 0.1),
        'min_child_weight': hp.quniform('min_child_weight', 0, 10, 1),
        'max_depth': hp.quniform('max_depth', 1, 10, 1),
        'subsample': hp.quniform('subsample', 0.5, 1, 0.1),
        'colsample_bytree': hp.quniform('colsample_bytree', 0.1, 1, 0.1),
        'num_round': hp.quniform('num_round', 10, 500, 10),
        'silent': 1
    }

    best = fmin(score, space2, algo=tpe.suggest, trials=trials, max_evals=2)

    return best

# loading features
X_train_file = 'geodata/poi_data/x_train.pkl'
y_train_file = 'geodata/poi_data/y_train.pkl'
X_test_file = 'geodata/poi_data/x_test.pkl' 
y_test_file = 'geodata/poi_data/y_test.pkl'

with open(X_train_file, 'rb') as f:
    X_train = cPickle.load(f)

with open(y_train_file, 'rb') as f:
    y_train = cPickle.load(f)

with open(X_test_file, 'rb') as f:
    X_test = cPickle.load(f)

with open(y_test_file, 'rb') as f:
    y_test = cPickle.load(f)

# Trials object where the history of search will be stored
trials = Trials()

best_param = optimize(trials)

run_model(best_param)
print best_param

parameters = ['eta', 'gamma', 'min_child_weight', 'max_depth', 'subsample', 'colsample_bytree', 'num_round']
# parameters = ['eta', 'lambda', 'alpha', 'lambda_bias', 'num_round']
cols = len(parameters)
f, axes = plt.subplots(nrows=1, ncols=cols, figsize=(40, 7))
cmap = plt.cm.jet
for i, val in enumerate(parameters):
    xs = np.array([t['misc']['vals'][val] for t in trials.trials]).ravel()
    ys = [t['result']['loss'] for t in trials.trials]
    xs, ys = zip(*sorted(zip(xs, ys)))
    axes[i].scatter(xs, ys, s=20, linewidth=0.01, alpha=0.25, c=cmap(float(i) / len(parameters)))
    axes[i].set_title(val)
    axes[i].set_ylim([0.1, 0.4])

learn_fig = './learn.png'
savefig(learn_fig)
plt.show()
