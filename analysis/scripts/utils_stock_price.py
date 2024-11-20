import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

class UtilsStockPrice(ABC):
    @abstractmethod
    def average_return(ticker: pd.DataFrame, date: np.datetime64, offset: int = 0, window: int = 1) -> float:
        
        pass