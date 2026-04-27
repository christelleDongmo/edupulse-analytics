import numpy as np

def moyenne(x): return np.mean(x)
def variance(x): return np.var(x)
def ecart_type(x): return np.std(x)
def quartiles(x): return np.percentile(x, [25, 50, 75])