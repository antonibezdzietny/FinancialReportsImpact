import pandas as pd
import numpy as np

class EDD:
    @staticmethod
    def pctl(returns: np.ndarray, n: int = 5):
        return np.array([np.sum( (np.sign(returns[i]) * \
            (returns[i] - returns[np.max([i-n, 0]): i]) > 0) ) / n 
            for i, _ in enumerate(returns)])

    @staticmethod
    def abr(returns: np.ndarray, ns = 5, nl = 30):
        return EDD.pctl(returns, nl) * EDD.pctl(np.abs(returns), nl) * \
               EDD.pctl(returns, ns) * EDD.pctl(np.abs(returns), ns)