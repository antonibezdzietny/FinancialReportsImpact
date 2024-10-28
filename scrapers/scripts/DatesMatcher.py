"""
Dates matcher generate map for casting YYYY/QN (quarterly) ->  YYYY:MM:DD (daily)
"""

import pandas as pd
import numpy as np

class DatesMatcher: 
    """
        Class match date format YYYY/QN (quarterly) ->  YYYY:MM:DD (daily)

        If nesesery custom your own function data_source. 
        Function should return date for concrete company in list in format YYYY:MM:DD
    """
    
    @staticmethod
    def dates_matcher(q_dates : list[str], d_dates : np.ndarray) -> list[str]:
        d_dates = d_dates.astype(np.datetime64)

        dates_mapper = pd.DataFrame(columns=["Q_DATES"], data= q_dates) 
        mapping_day = np.full(shape=len(q_dates), fill_value=pd.NA)

        
        for idx, row in dates_mapper.iterrows():
            q_year = row["Q_DATES"][:4]
            q_quarter = row["Q_DATES"][5:]
            
            match q_quarter:
                case "Q1":
                    math_d_date = d_dates[(d_dates >= np.datetime64(f"{q_year}-01-01")) & 
                                        (d_dates < np.datetime64(f"{q_year}-04-01"))]
                case "Q2":
                    math_d_date = d_dates[(d_dates >= np.datetime64(f"{q_year}-04-01")) & 
                                        (d_dates < np.datetime64(f"{q_year}-07-01"))]
                case "Q3":
                    math_d_date = d_dates[(d_dates >= np.datetime64(f"{q_year}-07-01")) & 
                                        (d_dates < np.datetime64(f"{q_year}-10-01"))]
                case "Q4":
                    math_d_date = d_dates[(d_dates >= np.datetime64(f"{q_year}-10-01")) & 
                                        (d_dates < np.datetime64(f"{int(q_year)+1}-01-01"))]
                    
                
            if len(math_d_date) > 0:
                mapping_day[idx] = math_d_date[0]

        dates_mapper["D_DATES"] = mapping_day
        return dates_mapper