import random
import numpy as np

SEED = 42
random.seed(SEED)
np.random.seed(SEED)


def rmse(y, p):
    return float(np.sqrt(np.mean((np.asarray(y) - np.asarray(p)) ** 2)))


def summarize(vals):
    v = np.asarray(vals)
    return {"mean": float(v.mean()), "best": float(v.min()), "worst": float(v.max()), "std": float(v.std(ddof=1))}


def paired_gain(base, model):
    """Per-seed RMSE improvement of model over baseline (positive = model better)."""
    d = np.asarray(base) - np.asarray(model)
    return float(d.mean()), float(d.std(ddof=1))
