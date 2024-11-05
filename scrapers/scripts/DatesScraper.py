import numpy as np
import pandas as pd
import requests
import re


class DatesScraper:
    def __init__(self):
        self.notoriaIDs = pd.read_csv("../database/designData/notoriaIDs.csv")

    def __cast_espi_title(self, title):
        year = re.findall("\\d{4}", title)

        if "SA-R" in title or "SA-RS" in title:
            return f"{year[0]}/R"
        elif "QSr1" in title or "QS 1" in title or "Q1" in title or "Q 1" in title:
            return f"{year[0]}/Q1"
        elif "QSr2" in title or "QS 2" in title or "Q2" in title or "Q 2" in title or "P" in title or "PS" in title:
            return f"{year[0]}/Q2"
        elif "QSr3" in title or "QS 3" in title or "Q3" in title or "Q 3" in title:
            return f"{year[0]}/Q3"
        elif "QSr4" in title or "QS 4" in title or "Q4" in title or "Q 4" in title:
            return f"{year[0]}/Q4"
        
    def __check_request_status_code(self, response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return "Error: " + str(e)
        
    def __get_id_locally(self, ticker):
        try:
            notoriaId = self.notoriaIDs[self.notoriaIDs["Ticker"] == ticker]["NotoriaID"].item()
        except:
            notoriaId = None
        return notoriaId
    
    def __get_id_remote(self, ticker):
        response = requests.get(f"https://www.notoria.pl/api/nol/search/news-issuer?phrase={ticker}") 
        self.__check_request_status_code(response)
        notoriaId = response.json()[0]["id"]
        return notoriaId

    def __get_id(self, ticker):
        # Try to get locally
        notoriaId = self.__get_id_locally(ticker)
        if notoriaId == None:
            notoriaId = self.__get_id_remote(ticker)
        return notoriaId

    def get_date_map(self, ticker):
        notoriaId = self.__get_id(ticker)

        # GET financial ESPI data 
        response = requests.get(f"https://www.notoria.pl/api/nol/news/espi-ebi?offset=0&limit=1000&notoriaId={notoriaId}&source=espi&type=5&category=6")
        self.__check_request_status_code(response)

        # Data customization
        espi_reports = pd.DataFrame(response.json()["result"][::-1])[["title", "published"]]
        espi_reports["published"] = espi_reports["published"].apply(lambda x : np.datetime64(x[:10]))
        espi_reports["title"] = espi_reports["title"].apply(lambda x : self.__cast_espi_title(x))
        espi_reports = espi_reports.dropna()
        espi_reports = espi_reports.drop_duplicates(subset="title")
        espi_reports.columns = ["Q_DATE", "D_DATE"]
        espi_reports = espi_reports.set_index("Q_DATE")

        return espi_reports
