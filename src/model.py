import random
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

SEED = 42
random.seed(SEED)
np.random.seed(SEED)


def baseline_predict(X, over_mark):
    """Week-4 baseline: current run rate held flat for all 20 overs. Uses runs_so_far/over_mark so it works for any feature set."""
    return X["runs_so_far"].values / over_mark * 20


def make_model(seed):
    return GradientBoostingRegressor(n_estimators=150, max_depth=3, learning_rate=0.05,
                                     subsample=0.8, random_state=seed)
