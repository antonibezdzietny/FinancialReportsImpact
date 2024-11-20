import pandas as pd
import numpy as np
from abc import ABC, abstractmethod


class StockDatabase():
    def __init__(self):
        self._historical_db = dict()


    def __read_csv_historical_data(self, ticker: str) -> pd.DataFrame:
        historical = pd.read_csv(f"../database/stockPrice/{ticker}.csv", index_col=[0])
        historical.index = historical.index.astype("datetime64[s]")
        return historical


    def __update_historical_db(self, ticker: str, historical: pd.DataFrame) -> None:
        self._historical_db[ticker] = historical

    
    def __load_historical_data_to_db(self, ticker: str) -> None:
        historical = self.__read_csv_historical_data(ticker)
        self.__update_historical_db(ticker, historical)

    def load_historical_data(self, ticker: str | list) -> None:
        if type(ticker) == str:
            ticker = [ticker]

        for t in ticker:
            if t not in self._historical_db:
                self.__load_historical_data_to_db(t)


    def get_historical_data(self, ticker: str) -> pd.DataFrame:
        if ticker not in self._historical_db:
            self.__load_historical_data_to_db(ticker)

        return self._historical_db[ticker]
    

    def get_db_keys(self) -> list:
        return list(self._historical_db.keys())
    

    def get_common_begin_date(self, tickers: list = None):
        begin_date = np.datetime64("1970-01-01")
        if tickers == None: 
            for key in self._historical_db:
                begin_date = np.max([self._historical_db[key].index[0], begin_date])
        else:
            for ticker in tickers:
                historical = self.get_historical_data(ticker)
                begin_date = np.max([historical[key].index[0], begin_date])
    
        return begin_date


    def clear_db(self) -> None:
        self._historical_db.clear()



class UtilsStockPrice(ABC):
    @abstractmethod
    def average_return(historical_data: pd.DataFrame, date: np.datetime64, window: int = 1,
                       offset: int = 0, column: str = "Close") -> float:
        idx = np.sum(historical_data.index < date)
        max_row = historical_data.shape[0]
        st_mean = historical_data.iloc[np.max([idx-offset-window, 0]) : 
                                       np.max([idx-offset, 0])][column].mean()
        en_mean = historical_data.iloc[np.min([idx+offset, max_row]) : 
                                       np.min([idx+offset+window, max_row])][column].mean()
        return (st_mean - en_mean) / st_mean * 100
    

    @abstractmethod
    def sector_average_return(stock_db: StockDatabase, date: np.datetime64, to_omit: str | list[str],
                              window: int = 1, offset: int = 0, column: str = "Close") -> float:
        if type(to_omit) == str:
            to_omit = [to_omit]
        
        tickers = stock_db.get_db_keys()
        tickers = [ticker for ticker in tickers if ticker not in to_omit]

        cmps = []
        for ticker in tickers:
            cmps.append(UtilsStockPrice.average_return(stock_db.get_historical_data(ticker), 
                                                       date, window=window, offset=offset, column=column))
        return np.array(cmps).mean()