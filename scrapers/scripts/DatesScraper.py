import numpy as np
import pandas as pd
import requests
import re


class DatesScraper:
    @staticmethod
    def __cast_espi_title(title):
        year = re.findall("\\d{4}", title)

        if "SA-R" in title or "SA-RS" in title:
            return f"{year[0]}/R"
        elif "QSr1" in title or "QS 1" in title or "Q1" in title or "Q 1" in title:
            return f"{year[0]}/Q1"
        elif "QSr2" in title or "QS 2" in title or "Q2" in title or "Q 2" in title:
            return f"{year[0]}/Q2"
        elif "QSr3" in title or "QS 3" in title or "Q3" in title or "Q 3" in title:
            return f"{year[0]}/Q3"
        elif "QSr4" in title or "QS 4" in title or "Q4" in title or "Q 4" in title:
            return f"{year[0]}/Q4"
        
    @staticmethod
    def __check_request_status_code(response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return "Error: " + str(e)
        
    @staticmethod
    def get_date_map(ticker):
        # GET company id
        response = requests.get(f"https://www.notoria.pl/api/nol/search/news-issuer?phrase={ticker}") 
        DatesScraper.__check_request_status_code(response)
        notoriaId = response.json()[0]["id"]

        # GET financial ESPI data 
        response = requests.get(f"https://www.notoria.pl/api/nol/news/espi-ebi?offset=0&limit=1000&notoriaId={notoriaId}&source=espi&type=5&category=6")
        DatesScraper.__check_request_status_code(response)

        # Data customization
        espi_reports = pd.DataFrame(response.json()["result"][::-1])[["title", "published"]]
        espi_reports["published"] = espi_reports["published"].apply(lambda x : np.datetime64(x[:10]))
        espi_reports["title"] = espi_reports["title"].apply(lambda x : DatesScraper.__cast_espi_title(x))
        espi_reports = espi_reports.dropna()
        espi_reports = espi_reports.drop_duplicates(subset="title")
        espi_reports.columns = ["Q_DATES", "D_DATES"]

        return espi_reports